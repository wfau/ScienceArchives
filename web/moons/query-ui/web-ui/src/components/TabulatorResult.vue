<script setup lang="ts">
import {ref, reactive, onBeforeMount, useTemplateRef, computed, watchEffect} from 'vue';
import {TabulatorFull as Tabulator} from 'tabulator-tables'; //import Tabulator library
import {getPreferredTheme} from './theme'

import { getTabulatorData } from '@/api/get_result.ts'

const props = defineProps(['result_url'])

// const table = ref(null); //reference to your table element
const tabulator = ref<Tabulator | null>(null); //variable to hold your table
const numRows = ref()
// const tableData = reactive([]); //data for table to display

var tabledata = [];
const table = useTemplateRef('table')

const showRows = computed(() => {
    if (numRows.value) {
        let r = Math.min(1000, parseInt(numRows.value))
        return `Showing 1 to ${Intl.NumberFormat().format(r)} of ${Intl.NumberFormat('en-GB').format(numRows.value)} rows.`
    }
    return ''
})

onBeforeMount(async () => {
    const prefTheme = getPreferredTheme()
    if (prefTheme == 'light') {
        await import("tabulator-tables/dist/css/tabulator.min.css")
    }
    else {
        await import("tabulator-tables/dist/css/tabulator_midnight.min.css")
    }
})

watchEffect(async () => {
    if (props.result_url && table.value) {
        const tableData = await getTabulatorData(props.result_url)
        tabledata = tableData['data']
        numRows.value = tableData['numRows']

        tabulator.value = new Tabulator(
            table.value, 
            {
                layout: 'fitColumns',
                data: tabledata, //link data to table
                reactiveData:true, //enable data reactivity
                columns:tableData['columns'],
                movableColumns: true,
            }
        );
        }
})

</script>

<template>
    <div class="m-4">
        <div>{{ showRows }}</div>
        <div id="table" ref="table"></div>
    </div>
</template>

<style scoped>
#table {
    height: 60vh;
}
</style>
