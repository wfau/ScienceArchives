import { headers, api_url } from './query'

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

export const getSpectrumData = async(url:string) => {
    const response = await fetch(url)
    if (response.status == 200) {
        return await response.text()
    } else {
        return null
    }

}