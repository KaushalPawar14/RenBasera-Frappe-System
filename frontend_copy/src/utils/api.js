import axios from "axios";
const api = axios.create({
	// Change this:
	// baseURL: 'http://192.168.3.144:8000/api/method',

	// To this:
	baseURL: "/api/method",
	headers: {
		"Content-Type": "application/json",
		Accept: "application/json",
	},
});

// Immediately load keys on app startup if they exist
const apiKey = localStorage.getItem("api_key");
const apiSecret = localStorage.getItem("api_secret");

if (apiKey && apiSecret) {
	api.defaults.headers.common["Authorization"] = `token ${apiKey}:${apiSecret}`;
}

export default api;
