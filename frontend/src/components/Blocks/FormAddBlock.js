import {html} from "../../html.js";
import { makeRequestBlock } from "../../utils/blocks.js";

export default (props) => {
    return {
        template: html`
            <form id="form-add-block" class="d-flex">
                <div>
					<custom-input icon="fa fa-user" type="text" required="yes" id="username">Enter username</custom-input>
                </div>
                <div>
					<button
                        id="btn-add-block"
                        class="btn btn-light btn-sm"
                        style="width: 100%; height: 100%"
                        type="submit"
                    >
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </form>
        `,
        handlers: [
            {
                selector: "#btn-add-block",
                event: "click",
                method: (e) => {
                    console.log(e)
                    const form = document.getElementById("form-add-block");
                    const formData = new FormData(form);
                    const username = formData.get("username");
                    makeRequestBlock(username, 'add');
                }
            }
        ]
    };
}