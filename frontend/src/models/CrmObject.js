import Model from "@/models/common.js";
import {formatDate} from "@/utils/helpers";
import {createObject, updateObject, updateObjectChildren} from "@/api/objects.js";

class CrmObject extends Model {
    constructor(description) {
        super(description)
        this._submissions = undefined
        this._exclude = ['children']
    }

    init(description) {
        super.init(description);

        if (!this.children) {
            this.children = []
        }
    }

    async save() {
        const children = this.children
        if (this.id) {
            this.init(await updateObject(this.id, this._present()))

        } else {
            this.init(await createObject(this.type, this._present()))
        }

        if (children?.length >= 0) {
            await this.saveChildren(children);
        }

        return this;
    }

    async saveChildren(children) {
        this.children = await updateObjectChildren(this.id, children.map(child => child.id))
    }

    async delete() {
        if (this.id) {
            await deleteObject(this.type, this.id)
        }
    }

    asChild() {
        return {
            id: this.id,
            type: this.type,
            name: this.name
        }
    }
}

export default CrmObject