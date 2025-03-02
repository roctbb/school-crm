import Model from "@/models/common.js";
import {formatDate} from "@/utils/helpers";
import {createObject, updateObject, updateObjectChildren} from "@/api/objects_api.js";
import {fetchObjectSubmissions} from "@/api/submissions_api.js";

class CrmObject extends Model {
    constructor(description, store) {
        super(description, store)
        this._exclude = ['children']
        this._submissions = []
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

        if (this.name !== this._backup.name) {
            for (const child of children) {
                const storeChild = this._store.getObject(child.type, child.id);
                if (storeChild) {
                    // Удаляем из массива parents этого потомка ссылку на текущий объект
                    const parent = storeChild.parents.find(parent => parent.id !== this.id);
                    parent.name = this.name;
                }
            }
        }


        if (children?.length >= 0) {
            await this.saveChildren(children);
        }

        return this;
    }

    async saveChildren(newChildren) {
        // Сначала вызываем ваш API, чтобы обновить детей на сервере.
        this.children = await updateObjectChildren(
            this.id,
            newChildren.map(child => child.id)
        );

        // Старый список детей (до сохранения).
        const oldChildren = this._backup.children || [];

        // 1. Ищем удалённых детей (были в старом списке, но нет в новом).
        const removedChildren = oldChildren.filter(
            oldChild => !this.children.some(newChild => newChild.id === oldChild.id)
        );

        // 2. Ищем добавленных детей (есть в новом списке, но не было в старом).
        const addedChildren = this.children.filter(
            newChild => !oldChildren.some(oldChild => oldChild.id === newChild.id)
        );

        // 3. Удаляем из родительского массива у «удалённых» детей
        for (const removedChild of removedChildren) {
            const storeChild = this._store.getObject(removedChild.type, removedChild.id);
            if (storeChild) {
                // Удаляем из массива parents этого потомка ссылку на текущий объект
                storeChild.parents = storeChild.parents.filter(
                    parent => parent.id !== this.id
                );
            }
        }

        // 4. Добавляем ссылку на «родителя» у новых детей
        for (const addedChild of addedChildren) {
            const storeChild = this._store.getObject(addedChild.type, addedChild.id);
            if (storeChild) {
                // Проверяем, нет ли уже такого родителя (чтобы не было дублей)
                if (!storeChild.parents.some(parent => parent.id === this.id)) {
                    storeChild.parents.push(this.asChild());
                }
            }
        }

        // 5. Обновляем резервную копию (чтобы в следующий раз корректно сравнивать)
        this._backup.children = [...this.children];
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

    async loadSubmissions() {
        if (this.id && this._submissions?.length === 0) {
            this._submissions = await fetchObjectSubmissions(this.id)
        }
    }
}

export default CrmObject