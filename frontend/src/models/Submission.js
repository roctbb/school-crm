import Model from "@/models/common.js";
import {createSubmission, deleteSubmission, updateSubmission} from "@/api/submissions_api.js";

class Submission extends Model {
    constructor(description, store) {
        super(description, store);
        this._exclude = [];
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