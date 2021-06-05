const APP_API_BASE_URL = 'http://localhost:8000';
const baseUrl = `${APP_API_BASE_URL}/api/main/option`;

const getOptions = () => {
    return axios({
        method: 'GET',
        url: `${baseUrl}/`
    })
}

export { getOptions };