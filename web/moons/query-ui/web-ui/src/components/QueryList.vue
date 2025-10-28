<script setup lang="ts">
import { ref, watch, onMounted, onBeforeMount, useTemplateRef } from 'vue'
import { api_url, headers } from '@/api/query'
import router from '@/router/index'

import {getPreferredTheme} from './theme'

import {TabulatorFull as Tabulator} from 'tabulator-tables'; //import Tabulator library
import { DateTime } from "luxon";

const table = useTemplateRef('queries-table')

onBeforeMount(async () => {
    const prefTheme = getPreferredTheme()
    if (prefTheme == 'light') {
        await import("tabulator-tables/dist/css/tabulator.min.css")
    }
    else {
        await import("tabulator-tables/dist/css/tabulator_midnight.min.css")
    }
})

onMounted(() => {
  
  if (table.value) {
  var tabulator = new Tabulator(table.value, {
      // @ts-ignore
      dependencies:{
        DateTime:DateTime,
      },
      layout: 'fitColumns',
      columns:[
        {
          title: 'Query',
          field:'query',
          formatter:'textarea',
          widthGrow: 4,
        },
        {
          title: 'Status',
          field:'current_status',
          headerSort:false,
          formatter:function(cell, formatterParams){
            var value = cell.getValue();

            switch (value) {
              case "Error":
                cell.getElement().classList.add('bg-danger')
                cell.getElement().classList.add('bg-opacity-10')
                break;
              case "Success":
                cell.getElement().classList.add('bg-success')
                cell.getElement().classList.add('bg-opacity-25')
                break;
              case "Running":
                cell.getElement().classList.add('bg-warning')
                cell.getElement().classList.add('bg-opacity-25')
                break;
              default:
                break;
            }
            return value;
          },
        },
        {
          title: 'Started',
          field:'started',
          formatter:"datetime", 
          formatterParams:{
            inputFormat:"iso",
            outputFormat:"dd/MM/yyyy HH:mm",
            invalidPlaceholder:"(invalid date)",
            timezone:"Europe/London",
          }
        },
        {
          title: 'Completed', field:'completed',
          formatter:"datetime", 
          formatterParams:{
            inputFormat:"iso",
            outputFormat:"dd/MM/yyyy HH:ss",
            invalidPlaceholder:"(invalid date)",
            timezone:"Europe/London",
          }
        },
        {
          title: 'Row count',
          field:'num_rows',
          hozAlign:"right",
        },
        {
          title: 'Results',
          field:'result_link',
          formatter:"html",
          headerSort:false,
        },
      ],
      pagination:true,
      paginationSize:20,
      paginationMode:"remote",
      sortMode:"remote",
      dataSendParams: {
        // 'sorters':'sort',
      },
      ajaxURL:api_url + '/queries', //set url for ajax request
      ajaxConfig:{
          headers: headers,
      },
      ajaxResponse:function(url, params, response){
        const newdata = response.data.map((obj:any) => {
          const resulturl = router.resolve({name: 'query-result', params: {id: obj.id}})
          // add the result link as a new column
          obj.result_link = `<a href="${resulturl.href}">html</a>`
          return obj
        })
        response.data = newdata
        return response; //return the response data to tabulator
      },
      ajaxURLGenerator:function(url, config, params){
        var purl = url + "?page=" + params.page + "&size=" + params.size
        params.sort.forEach((s: { dir: string; field: string }) => {
          purl += "&sort=" + (s.dir == 'asc'? '' : '-') + s.field
        });
        return purl
      },     
  });
  
    tabulator.on("rowClick", function(e, row) {
      router.push({name: 'query-result', params: {id: row.getData().id}})
    });
    tabulator.on("dataLoadError", function(error){
      const response = error as unknown as Response
      // if (response.status == 401) {
      //   window.location.replace('/oidc/authenticate')
      // }
      // if (response.status == 403) {
      //   window.location.replace('/oidc/authenticate')
      // }
    });
  }
})

</script>

<template>
  <div class="container">
    <h1>Your Queries</h1>

    <div id="table" ref="queries-table"></div>

  </div>

</template>
