<script setup lang="ts">
import { ref, onBeforeMount, watch} from 'vue'
import { useRoute } from 'vue-router'

import { getDatabaseSchema } from '@/api/schema';
import type { Schemas, Schema, TablesMap, TableDefinition } from '@/api/schema';

const currentTable = ref<TableDefinition>()
const currentSchema = ref<Schema>()

const tableSchema = ref<Schemas>()

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
                            <tr v-for="column, columnName in currentTable.columns">
                                <td>{{columnName}}</td>
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

</template>