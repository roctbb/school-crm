import Model from "@/models/common.js";
import {createSubmission, deleteSubmission, updateSubmission} from "@/api/submissions_api.js";

class Submission extends Model {
    constructor(description, store, form) {
        super(description, store);
        this._exclude = [];
        this._form = form;

        if (this.id && !this._form) {
            this._form = this._store.getForm(this.form.id)
        }
    }

    init(description) {
        super.init(description);
        if (!this.params) {
            this.params = {}; // JSON-объект параметров
        }
        if (!this.answers) {
            this.answers = {}; // JSON-объект ответов
        }
    }

    async save(objectId, formId) {
        this.showoff_attributes = {}

        for (let field of this._form.fields) {
            if (field.showoff && this.answers[field.code]) {
                this.showoff_attributes[field.name] = this.answers[field.code]
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
}

export default Submission;