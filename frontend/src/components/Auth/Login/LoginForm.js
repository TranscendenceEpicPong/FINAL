import { html } from "../../../html.js";
import { getUserInfo, postData } from "../../../api.js";
import { loadPage } from "../../../router.js";
import { setData } from "../../../store.js";
import { loadProfile } from "../../../utils/profile.js";
import {initAuth} from "../../../auth.js";

export default () => {
    return {
        template: html`
            <form>
                <div>
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
                <br />
                <div class="mt-3 d-flex justify-content-between">
                    <button type="submit" class="btn btn-primary">Login</button>
                    <button type="button" class="btn btn-light" id="btn-login-42">
                        42 login
                    </button>
                    <nav-link
                        style="color:white;display:flex;align-items:center;text-decoration:none;"
                        href="/auth/register"
                        >Not registered?</nav-link
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
                        `${process.env.BASE_URL}/authentication/login`,
                        reqBody
                    ).then(async (data) => {
                        console.log('LOGIN SUCCESS');
                        await initAuth();
                        await loadPage('/');
                    }).catch((err) => {
                        console.log('LOGIN ERROR');
                        console.error(err)
                        if (typeof err.status === "string" && err.status.toLowerCase() === "unauthorized") {
                            showToast("Nom d'utilisateur ou mot de passe incorrect")
                        }else{
                            loadPage('/auth/a2f');
                        }
                    })
                }
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
