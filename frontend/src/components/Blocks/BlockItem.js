import {html} from "../../html.js";

export default (props) => {
    const {name, avatar} = props;
    return {
        template: html`
            <div
            	class="d-flex justify-content-between align-items-center list-group-item">
            	<div class="d-flex align-items-center">
            		<img
            			class="rounded-circle"
            			src="${avatar}"
            			alt="Profile picture"
            			style="width: 48px; height: 48px" />
            		<div class="ml-3">
            			<strong class="d-block">${name}</strong
            			><small class="text-muted"
            				>${name}</small
            			>
            		</div>
            	</div>
            	<div class="d-flex">
					<remove-block-button username="${name}"></remove-block-button>
            	</div>
            </div>
        `,
    };
}