import Model from "@/models/common.js";
import {formatDate} from "@/utils/helpers";
import {createObject, updateObject} from "@/api/objects.js";

class CrmObject extends Model {
    constructor(description) {
        super(description)
        this._submissions = undefined
    }

    init(description) {
        super.init(description);
    }

    async save() {
        if (this.id) {
            this.init(await updateObject(this.id, this._present()))
        } else {
            this.init(await createObject(this.type, this._present()))
        }
        return this;
    }

    async delete() {
        if (this.id) {
            await deleteObject(this.type, this.id)
        }
    }
}

export default CrmObject