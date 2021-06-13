import {APP_API_BASE_URL} from '/static/api/urls.js';

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