import {html} from "../../html.js";
import {getUserInfo, postData} from "../../api.js";
import {loadPage} from "../../router.js";
import {setData} from "../../store.js";
import { loadProfile } from "../../utils/profile.js";

export default () => {
    return {
        template: html`
            <form>
                <div>
                    <custom-input id="code" icon="fa fa-qrcode" type="number" min="000000" max="999999" name="code"
                        >Enter your 2FA code</custom-input
                    >
                </div>
                <br />
                <div class="mt-3 d-flex justify-content-between">
                    <button type="submit" class="btn btn-primary">Connect</button>
                    <button id="link-change-account" class="btn btn-secondary">Change account</button>
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
                        `${process.env.BASE_URL}/authentication/check-code`,
                        reqBody
                    ).then(async (data) => {
                        await setData({auth: getUserInfo()}, {reload: false})
                        await loadProfile();
                        await loadPage('/');
                    }).catch((err) => {
                        console.error(err)
                        console.log(err.status);
                        if (err.status === 403) {
                            showToast(err.message);
                        }
                    })
                }
            },
            {
                selector: "#link-change-account",
                event: "click",
                method: async () => {
                    await postData(`${process.env.BASE_URL}/authentication/logout`);
                    await setData({auth: getUserInfo()}, {reload: false});
                    await loadPage('/auth/login');
                }
            }
        ],

    }
}