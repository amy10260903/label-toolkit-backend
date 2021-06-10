// const APP_API_BASE_URL = 'http://localhost:8000';
const APP_API_BASE_URL = 'http://140.114.27.13';
const baseUrl = `${APP_API_BASE_URL}/api/main/user`;

const userReport = (data) => {
    // console.log('data', data);
    return axios({
        method: 'POST',
        url: `${baseUrl}/`,
        data: data,
    })
}

export { userReport };