import Model from "@/models/common.js";
import {createForm, updateForm, deleteForm} from "@/api/forms_api.js";

class Form extends Model {
    constructor(description, store, categoryId) {
        super(description, store);
        this._exclude = [];
        this._categoryId = categoryId;
    }

    init(description) {
        super.init(description);
        if (!this.params) {
            this.params = {}; // Инициализация параметров по умолчанию
        }

        if (!this.fields) {
            this.fields = []; // Инициализация параметров по умолчанию
        }
    }

    async save() {
        if (this.id) {
            // Обновление формы
            this.init(await updateForm(this.id, this._present()));
        } else {
            // Создание новой формы
            this.init(await createForm(this._categoryId, this._present()));
        }
        return this;
    }

    async delete() {
        if (this.id) {
            await deleteForm(this.id); // Удаление формы по ID
        }
    }
}

export default Form;