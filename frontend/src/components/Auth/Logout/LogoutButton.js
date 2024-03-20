import {html} from "../../../html.js";
import {resetStore, setData} from "../../../store.js";
import {loadPage} from "../../../router.js";
import {getUserInfo, postData} from "../../../api.js";
import { resetSockets } from "../../../utils/socket.js";

export default (props) => {
    return {
        template: html`
            <button class="btn btn-danger">
                <i class="fa fa-sign-out"></i> Logout
            </button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: async () => {
                    const res = await postData(`${process.env.BASE_URL}/authentication/logout`);
                    resetSockets();
                    console.dir(window.store)
                    await resetStore();
                    console.dir(window.store)
                    return await loadPage("/auth/login");
                }
            }
        ]
    };
}