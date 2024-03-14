import { html } from "../../html.js";

export default () => {
	return html`
		<div
			style="display: flex; justify-content: center; align-items: center; height: 100vh;background: #252a2f;">
			<div
				class="shadow-lg"
				style="background-color:#171a1d;width:700px;padding:20px;border-radius:10px;color:#dfdfdf;">
				<div class="text-center">
					<h3 class="text-white">Welcome</h3>
					<h6>Join to play with your friends now!</h6>
				</div>
				<br />
				<register-form></register-form>
			</div>
		</div>
	`;
};