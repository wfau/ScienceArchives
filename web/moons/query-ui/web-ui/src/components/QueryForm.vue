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
import {getQueryTemplate, postQuery} from '@/api/query'
import router from '@/router/index'

import { getDatabaseSchema, type Schemas } from '@/api/schema';

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
        for (let tableName of Object.keys(cs.tables).sort()) {
            let data = cs.tables[tableName]
            result[tableName] = []
            for (let colName in data.columns) {
                result[tableName].push(colName)
            }
        }
        for (let viewName of Object.keys(cs.views).sort()) {
            let data = cs.views[viewName]
            result[viewName] = []
            for (let colName in data.columns) {
                result[viewName].push(colName)
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

const schemaData = ref<Schemas>()
const accessDenied = ref(false)

watch(schemaData, async (newSchema, oldSchema) => {
    if (newSchema) {
        accessDenied.value = false
        if (Object.keys(newSchema).length >= 1) {
            currentSchema.value = Object.keys(newSchema)[0]
        }
    }
    else if (newSchema === null) {
        accessDenied.value = true
    }
    var doc = 'SELECT '
    if (route.params.id) {
        const queryId = parseInt(route.params.id as string)
        const queryStatus = await getQueryResult(queryId)
        doc = queryStatus.query
        currentSchema.value = queryStatus.schema
    }
    else if (route.params.tid) {
        const templateId = parseInt(route.params.tid as string)
        const template = await getQueryTemplate(templateId)
        doc = template.query
        currentSchema.value = template.schema
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
    // schemaData.value = await getQuerySchema() as {[key: string]: {[key: string] : TableData }}
    schemaData.value = await getDatabaseSchema()
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
<div v-if="accessDenied" class="m-4 alert alert-danger">
    Access Denied
</div>
<div class="split left p-4" v-if="!accessDenied" >
    <h5>Database Schema</h5>
    <div>
        <ul class="tree">
        <li>
            <details open>
            <summary>GES</summary>
            <ul>
                <li v-for="(tableSchema, schemaName) in schemaData">
                    <details :open="schemaName == currentSchema">
                        <summary>{{ schemaName }}</summary>
                        <ul>
                            <li v-for="table of Object.entries({...tableSchema.tables, ...tableSchema.views}).sort()">
                                <details>
                                    <summary><span draggable="true" @dragstart="handleDragStart" :title="table[1].markdown && table[1].markdown[0].h">
                                        {{ table[0] }}
                                        <RouterLink :to="{ name: 'database-schema', query: {schema: schemaName, table: table[0]}}">
                                            <svg width="1em" height="1em" class="theme-icon-active">
                                                <use href="#icon-question" />
                                            </svg>
                                        </RouterLink>
                                    </span>
                                    </summary>
                                    <ul>
                                        <li v-for="col in table[1].columns">
                                            <span draggable="true" @dragstart="handleDragStart" :title="col.description">
                                                {{col.name}}
                                            </span>
                                            :
                                            <span class="fst-italic">{{col.type}}</span>
                                        </li>
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

<div class="split right p-4"  v-if="!accessDenied">

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
                Enter your freeform SQL query here or start with a <RouterLink :to="{ name: 'query-templates'}">Query Template</RouterLink>.
            </label>
            <div id="editor" ref="editor" class="form-control"></div>
        </div>

        <button class="btn btn-primary" value="Submit" @click="submit">Submit</button>

    </div>

</div>

<svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
    <symbol id="icon-question" fill="currentColor" viewBox="0 0 512 512">
    <!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.-->
    <path d="M464 256a208 208 0 1 0 -416 0 208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm256-80c-17.7 0-32 14.3-32 32 0 13.3-10.7 24-24 24s-24-10.7-24-24c0-44.2 35.8-80 80-80s80 35.8 80 80c0 47.2-36 67.2-56 74.5l0 3.8c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-8.1c0-20.5 14.8-35.2 30.1-40.2 6.4-2.1 13.2-5.5 18.2-10.3 4.3-4.2 7.7-10 7.7-19.6 0-17.7-14.3-32-32-32zM224 368a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/>
    </symbol>
</svg>


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
