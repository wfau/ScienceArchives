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

export const getAGGridResult = async (id: Number) => {
    const url = `${api_url}/results/${id}`
    const file = await asyncBufferFromUrl({ url, requestInit: {headers: headers} })
    const metadata = await parquetMetadataAsync(file)
    const schema = parquetSchema(metadata)
    const columnNames = schema.children.map(e => {
        const result = {
            field: e.element.name,
            type: 'leftAligned',
            title: e.element.name,
        }
        if (e.element.type == 'DOUBLE' || e.element.type == 'FLOAT' || e.element.type == 'INT32' || e.element.type == 'INT64' || e.element.type == 'INT96') {
            result['type'] = ''
        }
        return result
    })
    // console.log(metadata)
    // console.log(columnNames)
    let data = await parquetReadObjects({
        file,
        // rowStart: 0,
        // rowEnd: 4,
    })
    return {
        columns: columnNames,
        numRows: metadata.num_rows,
        data: data,
    }
    // .then((file) => {
    //     return parquetMetadataAsync(file)
    // })
    // .then((metadata) => {
    //     // Get total number of rows (convert bigint to number)
    //     const numRows = Number(metadata.num_rows)
    //     // Get nested table schema
    //     const schema = parquetSchema(metadata)
    //     console.log(schema)
    //     // Get top-level column header names
    //     const columnNames = schema.children.map(e => e.element.name)
    //     console.log(columnNames)
    //     // return parquetReadObjects({
    //     //     file,
    //     //     rowStart: 0,
    //     //     rowEnd: 4,
    //     // })

    // })
    // .catch((error) => {
    //     console.log(error)
    // })
    // const metadata = await parquetMetadataAsync(file)

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
    const file = await asyncBufferFromUrl({ url, requestInit: {headers: headers} })
    const metadata = await parquetMetadataAsync(file)
    const schema = parquetSchema(metadata)
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
    data.map((obj:any) => {
        const f = obj.filename
        if (f) {
            // get file link
            const resulturl = router.resolve({name: 'result-file', params: {id: id.toString()}})
            obj.filename = `<a href="${resulturl.href}?file=${f}">${f}</a>`
        }
    })
    return {
        columns: columnNames,
        numRows: metadata.num_rows,
        data: data,
    }
}

export const getSpectrumData = async(id: Number, filename: string) => {
    const url = `${api_url}/results/${id}/file?filename=${filename}`
    const response = await fetch(url)
    if (response.status == 200) {
        return await response.text()
    } else {
        return null
    }

}