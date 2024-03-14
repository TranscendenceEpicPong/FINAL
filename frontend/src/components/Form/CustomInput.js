import { html } from "../../html.js";

export default (props) => {
	const { id, icon, type, required, min, max, value, readonly, textContent } = props;
	return {
		template: html`
			<div id="custom-input">
				<i class="${icon} ml-3"></i
				><input
					type="${type}"
					name="${id}"
					id="${id}"
					class="ml-3"
					${required ? "required" : ""}
					${min ? `min=${min}` : ""}
					${max ? `max=${max}` : ""}
					${value ? `value=${value}` : ""}
					${readonly ? "readonly" : ""}
					placeholder="${textContent}" />
			</div>
		`,
	};
};