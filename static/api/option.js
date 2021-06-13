import {APP_API_BASE_URL} from '/static/api/urls.js';

const baseUrl = `${APP_API_BASE_URL}/api/main/option`;

const getOptions = () => {
    return axios({
        method: 'GET',
        url: `${baseUrl}/`
    })
}

export { getOptions };