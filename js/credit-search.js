function updateSearch(event)
{
    search_string = document.getElementById('search_input').value;
    search_items = document.getElementsByClassName('search_item');
    for (n = 0; n < search_items.length; n ++)
    {
        item = search_items[n];
        item_name = search_items[n].getElementsByClassName('item_name')[0].innerHTML;
        found = true;
        search_words = search_string.split(' ');
        for (i = 0; i < search_words.length; i ++)
        {
            search_word = search_words[i];
            if (item_name.toLowerCase().indexOf(search_word.toLowerCase()) == -1)
            {
                found = false;
            }
        }
        if (found == true)
        {
            item.style.display = "inherit";
        }
        else
        {
            item.style.display = "none";
        }
    }
}