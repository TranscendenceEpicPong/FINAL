import { html } from "../../html.js";

export default (props) => {
	return {
		template: html`
		<div class="menu-item mt-4">
				<h6
					style="
			margin-bottom: 0px;
			margin-left: 10px;
		">
					<i class="fa fa-heart"></i>&nbsp;<nav-link href="/friends" style="color: #aaaaaa;">New friends</nav-link>
				</h6>
				<span
					class="badge badge-pill badge-danger"
					style="
			margin-left: auto;
			margin-right: 10px;
		"
					>42</span
				>
		</div>`,
	};
};
