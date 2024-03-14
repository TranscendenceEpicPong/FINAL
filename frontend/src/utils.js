export function isObject(v) {
	return typeof v === "object" && !Array.isArray(v) && v !== null;
}

export function isArray(v) {
	return typeof v === "object" && Array.isArray(v) && v !== null;
}
