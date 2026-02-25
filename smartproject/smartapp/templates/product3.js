const categoriesSection = document.getElementById('categories-section');

// Handle new category creation
document.getElementById('category-form').addEventListener('submit', function(e){
    e.preventDefault();
    const name = document.getElementById('new-category-name').value;
    if(!name) return;

    createCategoryTable(name);
    document.getElementById('new-category-name').value = '';
});

function createCategoryTable(categoryName){
    const container = document.createElement('div');
    container.classList.add('category-container');

    container.innerHTML = `
        <h2>${categoryName}</h2>
        <button onclick="addRow(this)">Add Product</button>
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Barcode</th>
                    <th>Quantity</th>
                    <th>Source Warehouse</th>
                    <th>Available</th>
                    <th>Delete</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `;
    categoriesSection.appendChild(container);
}

function addRow(button){
    const tbody = button.nextElementSibling.querySelector('tbody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" placeholder="Product Name"></td>
        <td><input type="text" placeholder="Barcode"></td>
        <td><input type="number" placeholder="Quantity"></td>
        <td><input type="text" placeholder="Source Warehouse"></td>
        <td><input type="text" placeholder="Available"></td>
        <td><button onclick="deleteRow(this)">Delete</button></td>
    `;
    tbody.appendChild(row);
}

function deleteRow(button){
    button.closest('tr').remove();
}