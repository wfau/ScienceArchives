<script setup lang="ts">
import { ref, onBeforeMount, watch, computed} from 'vue'
import { useRoute } from 'vue-router'

import { getDatabaseSchema } from '@/api/schema';
import type { Schemas, Schema, TableDefinition } from '@/api/schema';

const currentTable = ref<TableDefinition>()
const currentSchema = ref<Schema>()

const tableSchema = ref<Schemas>()

const foreignKeys = computed(() => {
    const result:string[] = []
    for (const fk of (currentTable?.value?.references || [])) {
        result.push(...fk.sourceCol)
    }
    return result
})

const route = useRoute()
onBeforeMount(async () => {
    tableSchema.value = await getDatabaseSchema()
})

watch(tableSchema, async (newSchema, oldSchema) => {
    if (newSchema && route.query.schema && route.query.table) {
        currentSchema.value = newSchema[route.query.schema as string]
        const table = currentSchema.value.tables[route.query.table as string]
        const view = currentSchema.value.views[route.query.table as string]
        currentTable.value = table ? table : view
    }
})

</script>

<template>

    <main class="container-fluid">
        <h1>Schema Browser</h1>
        <div class="row">
            <div class="col-6 col-lg-4">
                <ul class="tree">
                <li v-for="(schema, schemaName) in tableSchema">
                     <details :open="schema == currentSchema">
                        <summary>{{ schemaName }}</summary>
                        <ul>
                            <li>
                                <details :open="schema == currentSchema && currentTable && currentTable.name in currentSchema.tables">
                                    <summary>Tables</summary>
                                    <ul>
                                        <li v-for="tableName in Object.keys(schema.tables).sort()"
                                            @click="()=>{currentSchema=schema; currentTable=schema.tables[tableName]}"
                                        >
                                            <span :class="(schema == currentSchema && tableName == currentTable?.name) ? 'text-primary' : ''">
                                            {{ tableName }}
                                            </span>
                                        </li>
                                    </ul>
                                </details>
                            </li>
                            <li>
                                <details :open="schema == currentSchema && currentTable && currentTable.name in currentSchema.views">
                                    <summary>Views</summary>
                                    <ul>
                                        <li v-for="tableName in Object.keys(schema.views).sort()" @click="()=>{currentSchema=schema; currentTable=schema.views[tableName]}">
                                            <span :class="(schema == currentSchema && tableName == currentTable?.name) ? 'text-primary' : ''">
                                            {{ tableName }}
                                            </span>
                                        </li>
                                    </ul>
                                </details>
                            </li>
                        </ul>
                    </details>
                </li>
                </ul>
            </div>
            <div class="col-6 col-lg-8">
                <div v-if="currentTable && currentSchema">
                    <div>{{ currentTable.schema }}</div>
                    <h2>{{ currentTable.name }}</h2>
                    <div>
                        <div v-for="item in currentTable.markdown">
                            <span v-for="(t,l) in item as object" :class="[ l == 'h' ? 'my-4 lead': '' ]" v-html="t"></span>
                        </div>
                    </div>
                    <div v-if="currentTable.primary_keys" class="mt-4">
                        <div class="fw-bold">Primary Keys</div>
                        <ul>
                            <li v-for="pk in currentTable.primary_keys">
                                <a :href="`#${pk}`">{{ pk }}</a>
                            </li>
                        </ul>
                    </div>
                    <div v-if="currentTable.references" class="mt-4">
                        <div class="fw-bold">Foreign Keys</div>
                        <ul>
                            <li v-for="fk in currentTable.references">
                                <a :href="`#${fk.sourceCol.join(', ')}`">{{ fk.sourceCol.join(', ') }}</a> &rarr;
                                <a :href="`#${fk.targetCol.join(', ')}`" @click="()=>{currentTable=currentSchema?.tables[fk.target]}">
                                    {{ fk.target }}.{{ fk.targetCol.join(', ') }}
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div v-if="currentTable.statement" class="mt-4">
                    <pre class="p-2 border rounded text-warning"><span v-for="item in currentTable.statement" v-html="item"></span></pre>
                    </div>
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th><th>Length</th><th>Unit</th>
                                <th>Description</th>
                                <th>Default Value</th>
                                <th>Unified Content Descriptor</th>
                                <th>Catalogue TType keyword</th>
                                <th>Image primary HDU keyword</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="column, columnName in currentTable.columns" :id="`${columnName}`">
                                <td>
                                    <template v-if="(currentTable.primary_keys || []).includes(columnName)">
                                        <span class="text-decoration-underline">{{ columnName }}</span>&nbsp;
                                        <svg width="1.5em" height="1.5em">
                                            <use href="#icon-key" />
                                        </svg>
                                    </template>
                                    <span v-else>
                                        {{ columnName }}
                                    </span>
                                    <template v-if="(foreignKeys || []).includes(columnName)">
                                        <sup class="fst-italic">FK</sup>
                                    </template>
                                </td>
                                <td>{{ column.type }}</td>
                                <td>{{ column.size }}</td>
                                <td>{{ column.unit }}</td>
                                <td v-html="column.description"></td>
                                <td>{{ column.default }}</td>
                                <td>{{ column.unified_content_descriptor }}</td>
                                <td class="text-break">{{ column.fits_ttype }}</td>
                                <td class="text-break">{{ column.casu_keyword }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <svg xmlns="http://www.w3.org/2000/svg">
      <symbol id="icon-key" fill="currentColor" viewBox="0 0 640 640">
          <!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.-->
        <path d="M400 416C497.2 416 576 337.2 576 240C576 142.8 497.2 64 400 64C302.8 64 224 142.8 224 240C224 258.7 226.9 276.8 232.3 293.7L71 455C66.5 459.5 64 465.6 64 472L64 552C64 565.3 74.7 576 88 576L168 576C181.3 576 192 565.3 192 552L192 512L232 512C245.3 512 256 501.3 256 488L256 448L296 448C302.4 448 308.5 445.5 313 441L346.3 407.7C363.2 413.1 381.3 416 400 416zM440 160C462.1 160 480 177.9 480 200C480 222.1 462.1 240 440 240C417.9 240 400 222.1 400 200C400 177.9 417.9 160 440 160z"/>
      </symbol>
    </svg>
</template>