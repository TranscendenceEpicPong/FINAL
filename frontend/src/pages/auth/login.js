import { html } from "../../html.js";

export default () => {
	return html`
		<div
			style="display: flex; justify-content: center; align-items: center; height: 100vh;background: #252a2f;">
			<div
				class="shadow-lg"
				style="background-color:#171a1d;width:700px;padding:20px;border-radius:10px;color:#dfdfdf;">
				<div class="text-center">
					<h3 class="text-white">Welcome back</h3>
					<h6>We are happy to see you again!</h6>
				</div>
				<br />
				<login-form></login-form>
			</div>
		</div>
	`;
};