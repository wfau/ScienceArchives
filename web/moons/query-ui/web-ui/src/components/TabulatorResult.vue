<script setup lang="ts">
import {ref, onBeforeMount, useTemplateRef, computed, watchEffect, watch} from 'vue';
import {TabulatorFull as Tabulator, type ColumnDefinition} from 'tabulator-tables'; //import Tabulator library
import {getPreferredTheme} from './theme'
import { DateTime } from "luxon";

import router from '@/router/index'
import { api_url } from '@/api/query'

const props = defineProps(['result_url', 'result_id'])

// const table = ref(null); //reference to your table element
const tabulator = ref<Tabulator | null>(null); //variable to hold your table
const numRows = ref()
// const tableData = reactive([]); //data for table to display

var tabledata = [];
const table = useTemplateRef('table')

onBeforeMount(async () => {
    const prefTheme = getPreferredTheme()
    if (prefTheme == 'light') {
        await import("tabulator-tables/dist/css/tabulator.min.css")
    }
    else {
        await import("tabulator-tables/dist/css/tabulator_midnight.min.css")
    }
})

const colSchema = ref()
const firstRow = ref()
const lastRow = ref()
const totalRows = ref()

var headerMenu = function(e:Event, component:any){
    var menu = [];
    var columns = component._column.table.getColumns();

    for(let column of columns){

        let icon = document.createElement("input");
        icon.setAttribute('type', 'checkbox')
        if (column.isVisible()) {
            icon.setAttribute('checked', 'true')
        }

        let label = document.createElement("span");
        let title = document.createElement("span");

        title.textContent = " " + column.getDefinition().title;

        label.appendChild(icon);
        label.appendChild(title);

        //create menu item
        menu.push({
            label:label,
            action:function(e:Event){
                //prevent menu closing
                e.stopPropagation();

                //toggle current column visibility
                column.toggle();

                //change menu item checkbox
                if(column.isVisible()){
                    icon.setAttribute('checked', 'true')
                }else{
                    icon.removeAttribute('checked')
                }
            }
        });
    }

   return menu;
};

watchEffect(async () => {
    if (props.result_url && table.value) {
        // const tableData = await getTabulatorData(props.result_url, props.result_id)
        tabulator.value = new Tabulator(table.value, {
            // @ts-ignore
            dependencies:{
                DateTime:DateTime,
            },
            layout: 'fitDataFill',
            // autoColumns: true,
            pagination:true,
            paginationSize:20,
            paginationMode:"remote",
            ajaxURL:api_url + `/results/${props.result_id}/json`,
            ajaxResponse:function(url, params, response){
                colSchema.value = response.schema
                firstRow.value = response.slice[0]+1
                lastRow.value = Math.min(response.count, response.slice[1])
                totalRows.value = response.count
                response.data.map((obj:any) => {
                    const f = obj.filename
                    if (f) {
                        // get file link
                        const downloadLoc = `${api_url}/results/${props.result_id}/file?filename=${f}`
                        const fn = f.split('/').pop()
                        const spectrumLoc = router.resolve({name: 'result-file', params: {id: props.result_id.toString()}})
                        obj.filename = fn
                        obj.download = `<a href="${downloadLoc}" class="download"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-download"/></svg></a>`
                        obj.spectrum_plot = `<a href="${spectrumLoc.href}?file=${f}"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-chart-line" /></svg></a>`
                    }
                })
                return response
            },
            ajaxURLGenerator:function(url, config, params){
                return url + "?page=" + params.page
            },
        });
        tabulator.value.on("dataLoaded", function(data){
            const columnNames:ColumnDefinition[] = []
            var hasFilename = false
            for (const name in colSchema.value) {
                const updatedDef:ColumnDefinition = {
                    title: name,
                    field: name,
                    headerMenu:headerMenu,
                }
                if (colSchema.value[name] == 'double') {
                    updatedDef['hozAlign'] = 'right'
                }
                if (name.toLowerCase() == 'filename') {
                    hasFilename = true
                    updatedDef['formatter'] = 'html'
                    updatedDef['headerSort'] = false
                }
                columnNames.push(updatedDef)
            }
            if (hasFilename) {
                columnNames.push(
                    {
                        field: 'download',
                        title: 'Download',
                        formatter: 'html',
                        headerSort: false,
                        headerMenu:headerMenu,
                    } as ColumnDefinition,
                    {
                        field: 'spectrum_plot',
                        title: 'Spectrum',
                        formatter: 'html',
                        headerSort: false,
                        headerMenu:headerMenu,
                    } as ColumnDefinition,
                )
            }
            tabulator.value?.setColumns(columnNames)
        });
    }
})

</script>

<template>
    <div class="m-4">
        <div>Showing rows {{ firstRow }} to {{ lastRow }} of {{ totalRows }}</div>
        <div id="table" ref="table"></div>
    </div>
</template>

<style scoped>
#table {
    height: 60vh;
}
</style>
