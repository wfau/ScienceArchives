import { asyncBufferFromUrl, parquetReadObjects, parquetMetadataAsync, parquetSchema } from 'hyparquet'
import { headers, api_url } from './query'
import router from '@/router/index'
import type { ColumnDefinition } from 'tabulator-tables'

export const getQueryResult = async(id: Number) => {    
    const url = `${api_url}/queries/${id}`
    const response = await fetch(
        url,
        {
            headers: headers,
        }
    )
    if (response.status == 200) {
        return await response.json()
    } else {
        return null
    }
}
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

export const getTabulatorData = async (url: string, id: Number) => {
    const file = await asyncBufferFromUrl({
        url,
        requestInit: {
            headers: {"Content-Type": "application/vnd.apache.parquet"}
        }
    })
    const metadata = await parquetMetadataAsync(file)
    const schema = parquetSchema(metadata)
    var hasFilenameCol = false
    const columnNames:ColumnDefinition[] = schema.children.map(e => {
        const result = {
            headerMenu:headerMenu,
            field: e.element.name,
            title: e.element.name,
        } as ColumnDefinition
        if (e.element.type == 'DOUBLE' || e.element.type == 'FLOAT' || e.element.type == 'INT32' || e.element.type == 'INT64' || e.element.type == 'INT96') {
            result['hozAlign'] = 'right'
        }
        if (e.element.name.toLowerCase() == 'filename') {
            result['formatter'] = 'html'
            result['headerSort'] = false
            hasFilenameCol = true
        }
        return result as ColumnDefinition
    })
    // console.log(metadata)
    // console.log(columnNames)
    let data = await parquetReadObjects({
        file,
        // rowStart: 0,
        // get a maximum of 1000 rows
        rowEnd: 1000,
    })
    if (hasFilenameCol) {
        columnNames.push(
            {
                headerMenu:headerMenu,
                field: 'download',
                title: 'Download',
                formatter: 'html',
                headerSort: false,
            } as ColumnDefinition,
            {
                headerMenu:headerMenu,
                field: 'spectrum_plot',
                title: 'Spectrum',
                formatter: 'html',
                headerSort: false,
            } as ColumnDefinition,
        )
    }
    data.map((obj:any) => {
        const f = obj.filename
        if (f) {
            // get file link
            const downloadLoc = `${api_url}/results/${id}/file?filename=${f}`
            const fn = f.split('/').pop()
            const spectrumLoc = router.resolve({name: 'result-file', params: {id: id.toString()}})
            obj.filename = fn
            obj.download = `<a href="${downloadLoc}" class="download"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-download"/></svg></a>`
            obj.spectrum_plot = `<a href="${spectrumLoc.href}?file=${f}"><svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-chart-line" /></svg></a>`
        }
    })
    return {
        columns: columnNames,
        numRows: metadata.num_rows,
        data: data,
    }
}

export const getSpectrumData = async(url:string) => {
    const response = await fetch(url)
    if (response.status == 200) {
        return await response.text()
    } else {
        return null
    }

}