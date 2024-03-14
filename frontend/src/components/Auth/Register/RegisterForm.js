import { html } from "../../../html.js";
import { getUserInfo, postData } from "../../../api.js";
import { loadPage } from "../../../router.js";
import { loadProfile } from "../../../utils/profile.js";
import { setData } from "../../../store.js";

export default () => {
	return {
		template: html`
			<form>
				<div>
					<div style="display: flex; align-items: center; gap: 20px;">
						<div
							id="avatar_preview"
							class="d-flex justify-content-center align-items-center pointer"
							style="width:80px; height:80px; border:#ffffff dashed 2px; border-radius:50%; background-size:cover; background-position:center;">
							<i
								class="fa fa-picture-o"
								style="font-size:30px;"></i>
						</div>
						<h6>Choose your avatar</h6>
					</div>
					<input
						type="file"
						id="avatar"
						accept="image/*"
						class="d-none" />
					<input
						type="hidden"
						name="avatar"
						id="avatar-base64"
						class="form-control" />
				</div>
				<div class="mt-3">
					<custom-input
						id="email"
						icon="fa fa-envelope"
						type="email"
						required="yes"
						>Enter your email</custom-input
					>
				</div>
				<div class="mt-3">
					<custom-input
						id="username"
						icon="fa fa-user"
						type="text"
						required="yes"
						>Enter your username</custom-input
					>
				</div>
				<div class="mt-3">
					<custom-input
						id="password"
						icon="fa fa-lock"
						type="password"
						required="yes"
						>Enter your password</custom-input
					>
				</div>
				<div class="mt-3">
					<custom-input
						id="confirm_password"
						icon="fa fa-lock"
						type="password"
						required="yes"
						>Confirm your password</custom-input
					>
				</div>
				<br />
				<div class="mt-3 d-flex justify-content-between">
					<button type="submit" class="btn btn-primary">
						Register
					</button>
					<button type="button" class="btn btn-light" id="btn-login-42">
						42 login
					</button>
					<nav-link
						style="color:white;display:flex;align-items:center;text-decoration:none;"
						href="/auth/login"
						>Already registered?</nav-link
					>
				</div>
			</form>
		`,
		handlers: [
			{
                selector: "form",
                event: "submit",
                method: (e) => {
                    const form = e.target;
                    const data = new FormData(form);
                    const reqBody = Object.fromEntries(data);


                    postData(
                        `${process.env.BASE_URL}/authentication/register`,
                        {...reqBody}
                    ).then(async (data) => {
                        await setData({auth: getUserInfo()}, {reload: false})
                        await loadProfile();
                        await loadPage('/');
                    }).catch((err) => {
                        let error = '';
                        console.error(err)
                        for (const [key, value] of Object.entries(err)) {
                            error += `${value}\n`;
                        }
                        showToast(error);
                    })
                }
            },
			{
				selector: 'input[type="file"]',
				event: "change",
				method: (e) => {
					const file = e.target.files[0];
					const reader = new FileReader();
					reader.onloadend = function () {
						document.getElementById("avatar_preview").innerHTML =
							"";
						document.getElementById("avatar_preview").style.border =
							"none";
						document.getElementById(
							"avatar_preview"
						).style.backgroundImage = `url(${reader.result})`;
						const canvas = document.createElement("canvas");
						const ctx = canvas.getContext("2d");
						const image = new Image();
						image.src = reader.result;
						image.onload = function () {
							canvas.width = 75;
							canvas.height = 75;
							ctx.drawImage(image, 0, 0, 75, 75);
							document.getElementById("avatar-base64").value =
								canvas.toDataURL();
						};
					};
					reader.readAsDataURL(file);
				},
			},
			{
				selector: "#avatar_preview",
				event: "click",
				method: () => {
					document.getElementById("avatar").click();
				},
			},
			{
                selector: "#btn-login-42",
                event: "click",
                method: () => {
                    window.location.href = `${process.env.BASE_URL}/authentication/login42`;
                }
            }
		],
	};
};
