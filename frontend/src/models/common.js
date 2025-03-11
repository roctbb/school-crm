import {formatDateTime} from "@/utils/helpers";

class Model {
    constructor(description, store) {
        this.init(description)
        this._exclude = []
        this._store = store;
    }

    init(description) {
        this._backup = description

        if (description) {
            for (let key of Object.keys(description)) {
                this[key] = description[key]
            }

            this.id = parseInt(description.id)

            if (description.created_at) {
                this.created_at = new Date(description.created_at)
            }

            if (description.updated_at) {
                this.updated_at = new Date(description.updated_at)
            }
        }
    }

    save() {

    }

    reset() {
        this.init(this._backup)
    }

    _present() {
        const descrition = {}

        for (let key of Object.keys(this)) {
            if (typeof this[key] !== "function" && !key.startsWith("_") && !this._exclude.includes(key)) {
                descrition[key] = this[key]
            }
        }

        return descrition
    }

    copy() {
        const description = this._present()
        description.id = undefined
        console.log(description)
        return new this.constructor(description, this._store)
    }
}

export default Model