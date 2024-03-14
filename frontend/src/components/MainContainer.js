import { html } from "../html.js";
import { getData } from "../store.js";

export default (props) => {
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div style="display: flex; justify-content: center; align-items: center; height: 90%">
						<img src="/assets/img/42_logo.svg" alt="Logo" style="width: 200px;">
					</div>
				</div>
			</div>
		`,
	};
};
