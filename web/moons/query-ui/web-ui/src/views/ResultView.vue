<script setup lang="ts">
import { asyncBufferFromUrl, parquetReadObjects, parquetMetadataAsync, parquetSchema } from 'hyparquet'
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import QueryResult from '../components/QueryResult.vue'
import TabulatorResult from '@/components/TabulatorResult.vue'

const route = useRoute()

onMounted(async () => {

    // const resultId:Number = parseInt(route.params.id as string)
    // const table = await getQueryResult(resultId)
    // console.log(route.params.id)
    // const url = `http://localhost:9000/api/results/${route.params.id}`
    // const file = await asyncBufferFromUrl({ url })
    // const metadata = await parquetMetadataAsync(file)
    // // Get total number of rows (convert bigint to number)
    // const numRows = Number(metadata.num_rows)
    // // Get nested table schema
    // const schema = parquetSchema(metadata)
    // console.log(schema)
    // // Get top-level column header names
    // const columnNames = schema.children.map(e => e.element.name)
    // console.log(columnNames)
    // const data = await parquetReadObjects({
    //     file,
    //     rowStart: 0,
    //     rowEnd: 4,
    // })
    // console.log(data)
})
</script>

<template>

      <main>
        <QueryResult />
      </main>

</template>
