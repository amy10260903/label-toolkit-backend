let APP_API_BASE_URL;
const debug = false;
// const debug = true;

if (debug) {
    APP_API_BASE_URL = 'http://localhost:8000';
} else {
    APP_API_BASE_URL = 'http://localhost:8000';
    // APP_API_BASE_URL = 'http://140.114.27.13';
}

export { debug, APP_API_BASE_URL };