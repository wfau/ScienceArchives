export const api_url = 'http://localhost:9000/api'

export const headers = {
    "Content-Type": "application/json",
    // 'Authorization': 'Basic ' + btoa(username + ":" + password),
}

export const postQuery = (sqlQuery: string, schemaName: string | null, csrfToken: string ) => {
    const body = JSON.stringify({
        schema: schemaName,
        query: sqlQuery,
    })
    const url = api_url + '/queries'
    return fetch(url, {
        // credentials: "same-origin",
        // mode: "same-origin",
        method: "post",
        headers: {...headers, 'X-CSRFToken':csrfToken,},
        body: body,
    })
    .then(resp => {
        if (resp.ok) {
            return resp.json()
        } else {
            console.log("Status: " + resp.status)
            return Promise.reject(resp.status)
        }
    })
    .catch(err => {
        console.log(err)
    })
}

export type QueryTemplate = {
    id: number,
    name: string,
    schema: string,
    query: string,
    description: string,
}

export const getQueryTemplates = async() => {
    const url = `${api_url}/templates`
    const response = await fetch(
        url,
        {
            headers: headers,
        }
    )
    if (response.status == 200) {
        return response.json()
    }
}

export const getQueryTemplate = async(id: Number) => {
    const url = `${api_url}/templates/${id}`
    const response = await fetch(
        url,
        {
            headers: headers,
        }
    )
    if (response.status == 200) {
        return response.json()
    }
}
