import Model from "@/models/common.js";
import {createSubmission, deleteSubmission, updateSubmission} from "@/api/submissions_api.js";

class Submission extends Model {
    constructor(description, store, form) {
        super(description, store);
        this._exclude = [];
        this._form = form;

        if (this.id) {
            if (this.form.is_external) {
                this._form = {
                    name: this.form.name,
                    category: this.form.category,
                    is_external: true
                }
            }
            else {
                this._form = this._store.getForm(this.form.id)
            }
        } else {
            this.fields = [...this._form._category.common_fields, ...this._form.fields]
        }
    }

    init(description) {
        super.init(description);
        if (!this.params) {
            this.params = {}; // JSON-объект параметров
        }
        if (!this.fields) {
            this.fields = []; // JSON-объект ответов
        }
    }

    async save(objectId, formId) {
        this.showoff_attributes = {}

        for (let field of this.fields) {
            if (field.showoff && field.answer) {
                this.showoff_attributes[field.name] = field.answer
            }
        }

        if (this.id) {
            // Обновление существующего Submission
            this.init(await updateSubmission(objectId, this.id, this._present()));
        } else {
            // Создание нового Submission
            this.init(await createSubmission(objectId, formId, this._present()));
        }
        return this;
    }


    async delete(objectId) {
        if (this.id) {
            await deleteSubmission(objectId, this.id);
        }
    }

    copy() {
        const description = this._present()
        description.id = undefined
        return new this.constructor(description, this._store, this._form)
    }
}

export default Submission;