<script setup lang="ts">
import { useTemplateRef, ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

import { EditorState, Compartment } from '@codemirror/state';
import { indentWithTab, history, defaultKeymap, historyKeymap, cursorDocEnd } from '@codemirror/commands';
import { indentOnInput, indentUnit, bracketMatching, syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';
import { closeBrackets, autocompletion, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete';
import { lineNumbers, highlightActiveLineGutter, highlightSpecialChars, highlightActiveLine, keymap, EditorView } from '@codemirror/view';

// Theme
import { oneDark } from "@codemirror/theme-one-dark";

// Language
import { sql } from "@codemirror/lang-sql";

import { getQueryResult } from '@/api/get_result';

// query submission
import {postQuery} from '@/api/query'
import router from '@/router/index'

import { getQuerySchema } from '@/api/schema';

// edit query if provided
const route = useRoute()

type TableData = {
  data: (string | number)[][];
};
const currentSchema = ref<string | null>()

const editorTheme = new Compartment()

const csrfToken = ref('')

const codeSchema:any = computed(() => {
    var result:any = {}
    if (currentSchema.value && schemaData.value) {
        const cs = schemaData.value[currentSchema.value]
        for (let tableName of Object.keys(cs).sort()) {
            let data: TableData = cs[tableName]
            result[tableName] = []
            for (let col of data.data) {
                result[tableName].push(col[0])
            }
        }
    }
    return result
})

// get current theme (light or dark)
// this doesn't pick up a change
let theme = document.documentElement.getAttribute('data-bs-theme')
if (theme == 'auto') {
    theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const editor = useTemplateRef('editor')
const editorView= ref<EditorView | null>(null)

const schemaData = ref<{[key: string]: {[key: string] : TableData }}>()

watch(schemaData, async (newSchema, oldSchema) => {
    if (newSchema) {
        if (Object.keys(newSchema).length >= 1) {
            currentSchema.value = Object.keys(newSchema)[0]
        }
    }
    var doc = 'SELECT '
    if (route.params.id) {
        const queryId = parseInt(route.params.id as string)
        const queryStatus = await getQueryResult(queryId)
        doc = queryStatus.query
        currentSchema.value = queryStatus.schema
    }

    let sqlOptions = {
        upperCaseKeywords: true,
        schema: codeSchema.value,
    }

    let extensions = [
        lineNumbers(),
        highlightActiveLineGutter(),
        highlightSpecialChars(),
        history(),
        indentUnit.of("    "),
        indentOnInput(),
        bracketMatching(),
        closeBrackets(),
        autocompletion(),
        highlightActiveLine(),
        keymap.of([
            indentWithTab,
            ...closeBracketsKeymap,
            ...defaultKeymap,
            ...historyKeymap,
            ...completionKeymap,
        ]),
        sql(sqlOptions),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        editorTheme.of((theme == 'dark') ? oneDark : []),
    ];
    if (editor.value) {
        editorView.value = new EditorView({
            doc: doc,
            extensions,
            parent: editor.value })
    }
})

onMounted(async () => {
    schemaData.value = await getQuerySchema() as {[key: string]: {[key: string] : TableData }}
})

const handleDragStart = (e: Event) => {
    const data = e.target as HTMLElement
    const event = e as { dataTransfer?: DataTransfer } 
    event.dataTransfer?.setData('text', data.innerText);
}

const submit = () => {
    // console.log('submitting')
    const sqlQuery = editorView.value?.state.doc.toString()
    // console.log(sqlQuery)
    if (sqlQuery && currentSchema.value) {
        postQuery(sqlQuery, currentSchema.value, csrfToken.value)
        .then((jsonResponse) => {
            // store the id of the newly created query
            // console.log(jsonResponse)
            router.push({name: 'query-result', params: {id: jsonResponse.id}})
        })
        .catch((e) => console.log(e))
    }
}

var response = fetch('/api/csrf')
  .then((response) => {console.log(response); return response.text()})
  .then((text) => new DOMParser().parseFromString(text, "text/html"))
  .then((dom) => (<HTMLInputElement>dom.querySelector('[name=csrfmiddlewaretoken]'))?.value)
  .then((token => {
    csrfToken.value = token
  }));

</script>

<template>
<div class="split left p-4">
    <h5>Database Schema</h5>
    <div>
        <ul class="tree">
        <li>
            <details open>
            <summary>GES</summary>
            <ul>
                <li v-for="(tableSchema, schemaName) in schemaData">
                    <details>
                        <summary>{{ schemaName }}</summary>
                        <ul>
                            <li v-for="(table, name) in tableSchema">
                                <details>
                                    <summary><span draggable="true" @dragstart="handleDragStart">{{ name }}</span></summary>
                                    <ul>
                                        <li v-for="col in table.data"><span draggable="true" @dragstart="handleDragStart">{{col[0]}}</span>: <span class="fst-italic">{{col[1]}}</span></li>
                                    </ul>
                                </details>
                            </li>
                        </ul>
                    </details>
                </li>
                </ul>
            </details>
            </li>
        </ul>
    </div>
</div>

<div class="split right p-4">

    <div class="">

        <h1>Freeform SQL Query</h1>
    
        <p>This form allows you to submit an SQL query to the MOONS database.</p>
    
    </div>
    
    <div class="">

        <div>
            <label for="database-release">
                Select the database release to use: &nbsp;
            </label>
            <select v-model="currentSchema">
                <option v-for="(value, key) in schemaData" :value="key">
                    {{ key }}
                </option>
            </select>
        </div>

        <div id="div_id_editor" class="mb-3">
            <label for="editor" class="form-label">
                Query
            </label>
            <div id="editor" ref="editor" class="form-control"></div>
        </div>

        <button class="btn btn-primary" value="Submit" @click="submit">Submit</button>

    </div>


</div>
</template>

<style scoped>
/* Split the screen in half */
.split {
  height: 90%;
  position: fixed;
  z-index: 1;
  overflow: scroll;
}

/* Control the left side */
.left {
  left: 0;
  width: 30%;
}

/* Control the right side */
.right {
  right: 0;
  width: 70%;
}

#editor {
    height: 40vh;
    width: 100%;
}
/* Stretch editor to fit inside its containing div */
.cm-editor {
    height: 100%;
    width: 100%;
}

</style>
