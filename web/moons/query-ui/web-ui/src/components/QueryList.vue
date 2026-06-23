<script setup lang="ts">
import { ref, watch, onMounted, onBeforeMount, useTemplateRef } from 'vue'
import { api_url, deleteResult, headers } from '@/api/query'
import router from '@/router/index'

import {getPreferredTheme} from './theme'

import {TabulatorFull as Tabulator} from 'tabulator-tables'; //import Tabulator library
import { DateTime } from "luxon";

const table = useTemplateRef('queries-table')
const tabulator = ref<Tabulator>()

const deleteModal = ref(false)
const deleteId = ref()
const deleteMsg = ref()
const deleteError = ref(false)

const deleteQuery = (async () => {
    deleteModal.value = false
    deleteMsg.value = undefined
    deleteError.value = false
    try {
        await deleteResult(deleteId.value)
        deleteId.value = undefined
        deleteMsg.value = 'The query has been deleted.'
        deleteError.value = false
        setTimeout(() => {
            router.push({name: 'query-list'})
        }, 2000)
    } catch(err) {
        deleteMsg.value = 'There was a problem deleting the query.'
        deleteError.value = true
        deleteId.value = undefined
    } finally {
      await tabulator.value?.replaceData();
    }
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

onMounted(() => {
  try {
  if (!table.value) return;

  tabulator.value = new Tabulator(table.value, {
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
          title: 'Release',
          field:'schema',
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
            outputFormat:"dd/MM/yyyy HH:mm",
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
          title: "Actions",
          field: 'actions',
          formatter: function(cell, formatterParams, onRendered) {
            const queryId = cell.getRow().getData().id;
            const resulturl = router.resolve({name: 'query-result', params: {id: queryId}})
            return `
                <div class="actions-wrapper d-flex">
                  <a href="${resulturl.href}" class="view-btn w-50 d-flex align-items-center justify-content-center py-1">
                    View
                  </a>
                  <button class="delete-btn btn w-50 btn-outline-secondary text-danger">
                    <svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-bin"/></svg>
                  </button>
                </div>
              `;
          },
          width: 100,
          headerSort: false,
          hozAlign: "center",
          cellClick: function(e, cell) {
            e.stopPropagation();
            const target = e.target as HTMLElement;
            const viewBtn = target.closest(".view-btn");
            const deleteBtn = target.closest(".delete-btn");
            const rowData = cell.getRow().getData();
            if (viewBtn) {
              router.push({name: 'query-result', params: {id: rowData.id.toString() }})
            }
            if (deleteBtn) {
              console.log('delete')
              deleteId.value = rowData.id
              deleteModal.value = true
            }
          },
        },
      ],
      pagination:true,
      paginationSize:20,
      paginationMode:"remote",
      paginationCounter:"rows",
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
  
    tabulator.value.on("rowClick", function(e, row) {
      const target = e.target as Element;
      if (!target || target.closest('[tabulator-field="actions"]')) {
        return;
      }
      router.push({name: 'query-result', params: {id: row.getData().id}})
    });
    tabulator.value.on("dataLoadError", function(error){
      const response = error as unknown as Response
      // if (response.status == 401) {
      //   window.location.replace('/oidc/authenticate')
      // }
      // if (response.status == 403) {
      //   window.location.replace('/oidc/authenticate')
      // }
    });
    } catch (error) {
    console.error("Tabulator initialization failed during mount:", error);
  }

})

</script>

<template>
  <div class="container">
    <div class="d-flex justify-content-between">

      <h1>Your Queries</h1>
      <div>
        <button class="btn btn-primary"><RouterLink class="text-decoration-none text-reset" :to="{ name: 'query-form'}">New Query</RouterLink></button>
      </div>
    </div>

    <div v-if="deleteMsg" class="m-4 alert" :class="deleteError?'alert-danger':'alert-success'" role="alert">
      {{ deleteMsg }}
    </div>
    <div class="modal-backdrop" v-if="deleteModal" @click.self="deleteModal=false">
        <div class="modal-wrap">
            <div class="modal-dialog" @click.stop>
                <h5>Remove Query</h5>
                <div class="modal-body">
                    Would you like to delete this query and the results?
                    <div class="m-2 mt-4 text-center">
                        <button class="btn btn-danger m-1" @click="deleteQuery">Delete</button>
                        <button class="btn btn-secondary m-1" @click="deleteModal=false">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="table" ref="queries-table"></div>

  </div>

  <svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
      <symbol id="icon-bin" fill="currentColor" viewBox="0 0 640 640">
        <!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.-->
        <path d="M262.2 48C248.9 48 236.9 56.3 232.2 68.8L216 112L120 112C106.7 112 96 122.7 96 136C96 149.3 106.7 160 120 160L520 160C533.3 160 544 149.3 544 136C544 122.7 533.3 112 520 112L424 112L407.8 68.8C403.1 56.3 391.2 48 377.8 48L262.2 48zM128 208L128 512C128 547.3 156.7 576 192 576L448 576C483.3 576 512 547.3 512 512L512 208L464 208L464 512C464 520.8 456.8 528 448 528L192 528C183.2 528 176 520.8 176 512L176 208L128 208zM288 280C288 266.7 277.3 256 264 256C250.7 256 240 266.7 240 280L240 456C240 469.3 250.7 480 264 480C277.3 480 288 469.3 288 456L288 280zM400 280C400 266.7 389.3 256 376 256C362.7 256 352 266.7 352 280L352 456C352 469.3 362.7 480 376 480C389.3 480 400 469.3 400 456L400 280z"/>
      </symbol>
    </svg>

</template>
