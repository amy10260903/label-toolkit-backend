// const APP_API_BASE_URL = 'http://localhost:8000';
const APP_API_BASE_URL = 'http://140.114.27.13';
const baseUrl = `${APP_API_BASE_URL}/api/main/option`;

const getOptions = () => {
    return axios({
        method: 'GET',
        url: `${baseUrl}/`
    })
}

export { getOptions };