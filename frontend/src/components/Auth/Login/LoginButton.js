import {html} from "../../../html.js";
import {setData} from "../../../store.js";
import {loadPage} from "../../../router.js";

export default (props) => {
    const {method, textContent} = props;
    return {
        template: html`
            <button>${textContent}</button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: () => {
                    if (method === 'offline')
                    {
                        setData({
                            auth: {
                                loggedIn: false
                            },
                            mode: {
                                online: false
                            }
                        });
                    }
                    else
                    {
                        loadPage(`/auth/${method}`);
                    }
                }
            }
        ]
    };
}