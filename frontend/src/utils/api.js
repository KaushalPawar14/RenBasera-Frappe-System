const defaultHeaders = {
	Accept: "application/json",
	"Content-Type": "application/json",
	"X-Frappe-CSRF-Token": "fetch",
	"X-Requested-With": "XMLHttpRequest",
};

export async function apiGet(endpoint) {
	const res = await fetch(endpoint, {
		method: "GET",
		credentials: "include",
		headers: defaultHeaders,
	});
	if (!res.ok) {
		console.error(`API Error ${res.status} on ${endpoint}`);
		return { data: [] };
	}
	return res.json();
}

// POST for /api/resource/ (create/update documents)
export async function apiPost(endpoint, body) {
	const res = await fetch(endpoint, {
		method: "POST",
		credentials: "include",
		headers: defaultHeaders,
		body: JSON.stringify(body),
	});
	if (!res.ok) {
		console.error(`API Error ${res.status} on ${endpoint}`);
		return { data: null };
	}
	return res.json();
}

// PUT for /api/resource/ (update documents)
export async function apiPut(endpoint, body) {
	const res = await fetch(endpoint, {
		method: "PUT",
		credentials: "include",
		headers: defaultHeaders,
		body: JSON.stringify(body),
	});
	if (!res.ok) {
		console.error(`API Error ${res.status} on ${endpoint}`);
		return { data: null };
	}
	return res.json();
}

// GET with query params for /api/method/ calls — avoids 417
export async function apiMethod(method, params = {}) {
	const query = new URLSearchParams();
	for (const [key, val] of Object.entries(params)) {
		query.set(key, typeof val === "object" ? JSON.stringify(val) : val);
	}
	const url = `/api/method/${method}?${query.toString()}`;
	const res = await fetch(url, {
		method: "GET",
		credentials: "include",
		headers: defaultHeaders,
	});
	if (!res.ok) {
		console.error(`API Error ${res.status} on ${method}`);
		const data = await res.json().catch(() => ({}));
		return { message: null, exception: data.exception || `Error ${res.status}` };
	}
	return res.json();
}

export function listUrl(doctype, fields = ["name"], filters = [], limit = 50, orderBy = "") {
	const f = JSON.stringify(fields);
	let url = `/api/resource/${encodeURIComponent(doctype)}?fields=${encodeURIComponent(f)}&limit=${limit}`;
	if (filters.length) url += `&filters=${encodeURIComponent(JSON.stringify(filters))}`;
	if (orderBy) url += `&order_by=${encodeURIComponent(orderBy)}`;
	return url;
}
