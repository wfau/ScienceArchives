<script setup lang="ts">
import {ref, onBeforeMount, useTemplateRef, computed, watchEffect, watch} from 'vue';
import {TabulatorFull as Tabulator, type ColumnDefinition} from 'tabulator-tables'; //import Tabulator library
import {getPreferredTheme} from './theme'

import router from '@/router/index'
import { api_url } from '@/api/query'

const props = defineProps(['result_url', 'result_id', 'schema'])

const tabulator = ref<Tabulator | null>(null); //variable to hold your table

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
        tabulator.value = new Tabulator(table.value, {
            layout: 'fitDataFill',
            pagination:true,
            paginationSize:20,
            paginationMode:"remote",
            paginationCounter:"rows",
            sortMode:"remote",            
            ajaxURL:api_url + `/results/${props.result_id}/json`,
            ajaxResponse:function(url, params, response){
                colSchema.value = response.schema
                response.data.map((obj:any) => {
                    const f = obj.filename
                    const cname = encodeURIComponent(obj.cname)
                    if (f) {
                        // get file link
                        const downloadLoc = `${api_url}/results/${props.result_id}/file?filename=${f}`
                        obj.download = `<a href="${downloadLoc}" class="download"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-download"/></svg></a>`
                        const fn = f.split('/').pop()
                        obj.filename = fn
                    }
                    if (cname && cname != 'NONE') {
                        const spectrumLoc = router.resolve({name: 'result-file', params: {id: props.result_id.toString()}})
                        obj.spectrum_plot = `<a href="${spectrumLoc.href}?schema=${props.schema}&cname=${cname}"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-chart-line" /></svg></a>`
                    }
                })
                return response
            },
        });
        tabulator.value.on("dataLoaded", function(data){
            const columnNames:ColumnDefinition[] = []
            var hasTarget = false
            for (const name in colSchema.value) {
                const updatedDef:ColumnDefinition = {
                    title: name,
                    field: name,
                    headerMenu:headerMenu,
                    headerSort: false
                }
                if (colSchema.value[name] == 'double') {
                    updatedDef['hozAlign'] = 'right'
                }
                if (name.toLowerCase() == 'cname') {
                    hasTarget = true
                    updatedDef['formatter'] = 'html'
                }
                columnNames.push(updatedDef)
            }
            if (hasTarget) {
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
        <div id="table" ref="table"></div>
    </div>
</template>

<style scoped>
#table {
    height: 60vh;
}
</style>
