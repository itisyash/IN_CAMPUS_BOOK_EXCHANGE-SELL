function filterBooks() {
    const search = document.getElementById('search').value;
    const filter = document.getElementById('filter').value;
    fetch(`/filter_books?search=${search}&filter=${filter}`)
        .then(response => response.json())
        .then(data => {
            const booksList = document.getElementById('books-list');
            booksList.innerHTML = '';
            data.forEach(book => {
                booksList.innerHTML += `<li>${book.title} by ${book.author} - $${book.price}</li>`;
            });
        });
}