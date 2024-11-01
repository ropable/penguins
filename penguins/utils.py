def get_previous_pages(page_num, count=3):
    """Convenience function to take a Paginator page object and return the previous `count`
    page numbers, to a minimum of 1.
    """
    prev_page_numbers = []

    if page_num and page_num.has_previous():
        for i in range(page_num.previous_page_number(), page_num.previous_page_number() - count, -1):
            if i >= 1:
                prev_page_numbers.append(i)

    prev_page_numbers.reverse()
    return prev_page_numbers


def get_next_pages(page_num, count=3):
    """Convenience function to take a Paginator page object and return the next `count`
    page numbers, to a maximum of the paginator page count.
    """
    next_page_numbers = []

    if page_num and page_num.has_next():
        for i in range(page_num.next_page_number(), page_num.next_page_number() + count):
            if i <= page_num.paginator.num_pages:
                next_page_numbers.append(i)

    return next_page_numbers


def user_can_add_observations(user):
    """Passed-in User is authorised to create observations on videos."""
    if user.is_superuser:
        return True
    if "Observers" in user.groups.values_list("name", flat=True):
        return True
    return False


def breadcrumbs_html(links):
    """Returns HTML: an unordered list of URLs (no surrounding <ul> tags).
    ``links`` should be a iterable of tuples (URL, text).
    Reference: https://getbootstrap.com/docs/4.1/components/breadcrumb/
    """
    crumbs = ""
    li_str = '<li class="breadcrumb-item"><a href="{}">{}</a></li>'
    li_str_active = '<li class="breadcrumb-item active"><span>{}</span></li>'
    # Iterate over the list, except for the last item.
    if len(links) > 1:
        for i in links[:-1]:
            crumbs += li_str.format(i[0], i[1])
    # Add the final "active" item.
    crumbs += li_str_active.format(links[-1][1])
    return crumbs
