import { isArray } from "./utils.js";

function sanitize_html(input) {
	input = input.replace(/&/g, "&amp;");
	input = input.replace(/</g, "&lt;");
	input = input.replace(/>/g, "&gt;");
	input = input.replace(/"/g, "&quot;");
	input = input.replace(/'/g, "&#x27;");
	return input;
}

function renderTemplateElement(element) {
	if (
		Object.prototype.toString.call(element) !==
		"[object HTMLTemplateElement]"
	) {
		console.error("Cannot render this object: ", element);
		return "";
	}
	const childrenElements = Array.from(element.content.children);
	let content = "";
	childrenElements.forEach((el) => {
		content += el.outerHTML;
	});
	return content;
}

export function html(strings, ...values) {
	const template = document.createElement("template");
	let content = "";
	strings.forEach((s, i) => {
		content += s;
		let element = values[i];
		if (!element) return;
		switch (typeof element) {
			case "number":
				element = `${element}`;
			case "boolean":
				element = `${element ? '1' : '0'}`;
			case "string":
				content += sanitize_html(element);
				break;
			case "object":
				if (isArray(element)) {
					element.forEach(
						(el) => (content += renderTemplateElement(el))
					);
					break;
				}
				content += renderTemplateElement(element);
				break;
			default:
				console.error("Cannot interpret element ", element);
		}
	});
	content = content.trim();
	if (!content) return null;

	template.innerHTML = content;
	return template;
}
