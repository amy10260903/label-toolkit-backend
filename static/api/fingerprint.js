import {APP_API_BASE_URL} from '/static/api/urls.js';

const baseUrl = `${APP_API_BASE_URL}/api/main/fingerprint`;

const makeFormdata = (data) => {
    const passData = new FormData();
    Object.keys(data).forEach((key) => {
     passData.append(key, data[key])
    })
    return passData
}

const uploadFile = (data) => {
    // console.log('data', data);
    const params = makeFormdata(data);
    return axios({
        method: 'POST',
        url: `${baseUrl}/`,
        data: params,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export { uploadFile };