# -*- coding: utf-8 -*-
from django.test import TestCase

from xendor.models import Page, Setting
from xendor.structure import Structure
from xendor.settings import XendorSettings
from xendor.menu import Menu, _render_pars

#TestCase
class PageTest(TestCase):

    def _create_main_page(self):
        page = Page()
        page.title = u'New page, first page'
        page.content = u'First page content'
        page.save()

        return page


    def _create_page(self, number = 1):
        page = Page()
        page.title = u'Page number %s' % number
        page.save()


    def test_creating_page(self):
        """При создании страницы корректно сохраняются все введенные данные
        и проставляются значения по умолчанию"""

        self._create_main_page()

        #проверка на сохранение страницы
        pages = Page.objects.all()
        self.assertEqual(pages.count(), 1)
        main_page_in_db = pages[0]

        #проверка соотвествия полей необходимым данным
        self.assertEqual(main_page_in_db.title, u'New page, first page')
        self.assertEqual(main_page_in_db.content, u'First page content')
        self.assertEqual(main_page_in_db.visible, True)
        self.assertEqual(main_page_in_db.in_menu, True)
        self.assertEqual(main_page_in_db.app_extension, '')
        self.assertEqual(main_page_in_db.menu_title, '')
        self.assertEqual(main_page_in_db.menu_url, '')
        self.assertEqual(main_page_in_db.meta_title, '')
        self.assertEqual(main_page_in_db.meta_description, '')
        self.assertEqual(main_page_in_db.meta_keywords, '')


    def test_main_page_is_main_flag(self):
        """Первая созданная страница считается глвной и у нее проставляется флаг is_main"""

        self._create_main_page()

        pages = Page.objects.all()
        main_page_in_db = pages[0]

        #первая создаваемая страница по умолчанию становится главной
        self.assertEqual(main_page_in_db.is_main, True)


    def test_other_page_is_main_flag(self):
        """Все последующие страницы кроме первой имеют флаг is_main = False"""

        for i in range(10):
            self._create_page(i)

        pages = Page.objects.all().order_by('pk')

        self.assertEqual(pages[0].is_main, True)

        for i in range(2, 10):
            page = pages[i]
            #у всех остальных страниц флаг is_main отрицателен
            self.assertEqual(page.is_main, False)


        main_page = Page.objects.filter(is_main=True)
        self.assertEqual(main_page.count(), 1)


    def test_unable_second_main_page(self):
        """При попытках проставить флаг главной при уже существующей такой странице -
        втихую сливаем флаг в False"""

        #todo: предусмотреть потом валидацию в форме админки

        for i in range(10):
            self._create_page(i)

        new_main = Page()
        new_main.is_main = True
        new_main.save()

        pages = Page.objects.all().order_by('pk')

        self.assertEqual(pages[0].is_main, True)

        for i in range(2, 11):
            page = pages[i]
            #у всех остальных страниц флаг is_main отрицателен
            self.assertEqual(page.is_main, False)


        main_page = Page.objects.filter(is_main=True)
        self.assertEqual(main_page.count(), 1)


    def test_set_main_page(self):
        """Для того чтобы определить новую главную нужно снять флаг с предыдущей"""

        for i in range(10):
            self._create_page(i)

        main_page = Page.objects.get(is_main = True)
        main_page.is_main = False
        main_page.save()

        pages = Page.objects.all().order_by('pk')
        anoter_main = pages[pages.count() - 1]
        anoter_main.is_main = True
        anoter_main.save()

        main_page = Page.objects.filter(is_main=True)
        self.assertEqual(main_page.count(), 1)
        self.assertEqual(main_page[0], anoter_main)


    def test_make_subpage(self):
        """Создание подразделов"""

        main_page = self._create_main_page()

        roots = Page.objects.root_nodes()
        self.assertEqual(roots.count(), 1)
        self.assertEqual(roots[0], main_page)

        for i in range(10):
            subpage = Page(title=u'Subpage %s' % i, parent=main_page)
            subpage.save()

        subnodes = Page.objects.filter(level=1)

        self.assertEqual(subnodes.count(), 10)
        self.assertEqual(main_page.get_children().count(), 10)
        for i in range(10):
            self.assertEqual(subnodes[i].parent, main_page)


    def test_generate_page_slug_from_title(self):
        """Проверяем работоспособность генератора слагов из заголовка страницы на разных наборах значений"""

        #английский
        page = Page(title=u' English`s title for page ')
        page.save()
        self.assertEqual(page.slug, u'english-s-title-for-page')

        #русский
        page = Page(title=u' Английское название для страницы ')
        page.save()
        self.assertEqual(page.slug, u'anglijskoe-nazvanie-dlja-stranicy')

        #спецсимволы
        page = Page(title=u' @#@$@%%^*()page*#&#$&#*#$#*&#$title      ')
        page.save()
        self.assertEqual(page.slug, u'page-title')

        #пробелы
        page = Page(title=u' another                       page                          title ')
        page.save()
        self.assertEqual(page.slug, u'another-page-title')

        #дубликаты
        page1 = Page(title=u'  Заголовок')
        page2 = Page(title=u'Заголовок ')
        page3 = Page(title=u'Заголовок   ')
        page1.save()
        page2.save()
        page3.save()
        self.assertEqual(page1.slug, u'zagolovok')
        self.assertEqual(page2.slug, u'zagolovok-1')
        self.assertEqual(page3.slug, u'zagolovok-2')


    def test_generate_page_slug_from_slug(self):
        """Проверяем работоспособность генератора слагов из поля slug на разных наборах значений"""

        #английский
        page = Page(title=u'page')
        page.slug = u' English`s title for page '
        page.save()
        self.assertEqual(page.slug, u'english-s-title-for-page')

        #русский
        page = Page(title=u'page')
        page.slug = u' Английское название для страницы '
        page.save()
        self.assertEqual(page.slug, u'anglijskoe-nazvanie-dlja-stranicy')

        #спецсимволы
        page = Page(title=u'page')
        page.slug = u' @#@$@%%^*()page*#&#$&#*#$#*&#$title '
        page.save()
        self.assertEqual(page.slug, u'page-title')

        #пробелы
        page = Page(title=u'page')
        page.slug = u' another          page             title '
        page.save()
        self.assertEqual(page.slug, u'another-page-title')

        #дубликаты
        page1 = Page(title=u'page')
        page1.slug = u' Заголовок title  '
        page1.save()

        page2 = Page(title=u'page')
        page2.slug = u'     Заголовок    title'
        page2.save()

        page3 = Page(title=u'page')
        page3.slug = u'     Заголовок    title    '
        page3.save()

        self.assertEqual(page1.slug, u'zagolovok-title')
        self.assertEqual(page2.slug, u'zagolovok-title-1')
        self.assertEqual(page3.slug, u'zagolovok-title-2')


    def test_generate_page_slug_from_main(self):
        """Строим слаг раздела от главной страницы по заголовку страницы,
        слаг главной не должен фигурировать в слаге раздела"""

        main = self._create_main_page()

        page = Page(title=u'Subpage title', parent=main)
        page.save()

        self.assertEqual(page.slug, u'subpage-title' )


    def test_generate_subpage_slug_from_main(self):
        """Строим слаг подраздела от главной страницы по заголовку страницы"""

        main = self._create_main_page()

        page = Page(title=u'Subpage title', parent=main)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()
        self.assertEqual(subpage.slug, page.slug + '/' + u'sub-subpage-title' )


    def test_create_subpage_slug_from_main(self):
        """Строим слаг подраздела от главной страницы по полю slug,
        при этом к введенному слагу добавляется информация из структуры страниц"""

        main = self._create_main_page()

        page = Page(title=u'Subpage title', parent=main)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.slug = u'edited-slug'
        subpage.save()
        self.assertEqual(subpage.slug, page.slug + '/' + u'edited-slug')


    def test_edit_subpage_slug_from_main(self):
        """Редактируем слаг подраздела, при этом в слаге остается только явно введенное значение"""

        main = self._create_main_page()

        page = Page(title=u'Subpage title', parent=main)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()

        subpage.slug = u'edited-slug'
        subpage.save()
        self.assertEqual(subpage.slug, u'edited-slug')


    def test_generate_page_slug_for_exist_page(self):
        """При удалении слага слаг воссоздается заново с учетом положения в структуре страниц"""

        main = self._create_main_page()

        page = Page(title=u'Subpage title', parent=main)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()

        subpage.slug = u'edited-slug'
        subpage.save()
        self.assertEqual(subpage.slug, u'edited-slug')

        subpage.slug = u''
        subpage.save()
        self.assertEqual(subpage.slug, page.slug + '/' + u'sub-subpage-title')


    def test_generate_subpage_slug_from_root(self):
        """Строим слаг от другого корня (не главной страницы), при этом в слаге должна сохраняться информация о родителе"""

        self._create_main_page()

        root = Page(title=u'Page title')
        root.save()

        page = Page(title=u'Subpage title', parent=root)
        page.save()
        self.assertEqual(page.slug, root.slug + '/' + u'subpage-title' )

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()
        self.assertEqual(subpage.slug, page.slug + '/' + u'sub-subpage-title' )


    def test_generate_subpage_slug_with_not_visible_ancestors(self):
        """Строим слаг при наличии черновиков в анцесторах,
        все что выше visible=False в структуре слага не отображается"""

        self._create_main_page()

        root = Page(title=u'root Page title')
        root.save()

        subroot = Page(title=u'Not visible page', parent=root)
        subroot.visible = False
        subroot.save()

        page = Page(title=u'Subpage title', parent=subroot)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()
        self.assertFalse(u'/not-visible-page/' in subpage.slug)


    def test_generate_subpage_slug_with_not_in_menu_ancestors(self):
        """Строим слаг при наличии скрытых из меню нодов в анцесторах,
        в структуре слага не отображаются только ноды скрытые из меню"""

        self._create_main_page()

        root = Page(title=u'Root')
        root.save()

        subroot = Page(title=u'Not in menu page', parent=root)
        subroot.in_menu = False
        subroot.save()

        page = Page(title=u'Subpage title', parent=subroot)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()
        self.assertFalse('/not-in-menu-page/' in subpage.slug)


    def test_delete_page(self):
        """Удаляем нод и проверяем, что все потомки тоже удалились"""

        main = self._create_main_page()

        root = Page(title=u'Root', parent=main)
        root.save()

        subroot = Page(title=u'Page title', parent=root)
        subroot.in_menu = False
        subroot.save()

        page = Page(title=u'Subpage title', parent=subroot)
        page.save()

        subpage = Page(title=u'Sub-subpage title', parent=page)
        subpage.save()

        pages = Page.objects.all()
        self.assertEqual(pages.count(), 5)

        subroot.delete()

        pages = Page.objects.all()
        self.assertEqual(pages.count(), 2)


    def test_set_extension(self):
        """Ассоциируем модуль странице (просто прописываем id модуля в соотвествующее поле)"""

        page = self._create_main_page()

        self.assertEqual(page.app_extension, '')

        page.app_extension = u'news'
        page.save()

        self.assertEqual(page.app_extension, u'news')


    def test_set_same_extension_anoter_page(self):
        """При попытке ассоциировать уже ассоциированный модуль втихую сливаем в '' """

        page = self._create_main_page()
        page.app_extension = u'news'
        page.save()

        anoter_page = self._create_main_page()
        anoter_page.app_extension = u'news'
        anoter_page.save()

        self.assertEqual(page.app_extension, u'news')
        self.assertEqual(anoter_page.app_extension, '')


    def test_generate_slug_from_long_title(self):
        """Генерация правильного слага по очень длинному тайтлу"""

        page = Page(title=u'''Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title ''')

        page.save()

        self.assertLess(len(page.slug), 250)


    def test_generate_slug_from_long_slug(self):
        """Генерация правильного слага по очень длинному введенному значению слага"""

        page = Page(title=u'Page title')
        page.slug = u'''
        Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        Very long Title Very long Title Very long Title Very long Title Very long Title Very long Title
        '''

        page.save()

        self.assertLess(len(page.slug), 250)


#TestCase
class StructureTest(TestCase):

    def _create_pages(self):
        """Создаем некоторое дерево страниц"""
        for i in range(3):
            root = Page(title = u'Root %s' % i)
            root.save()

            for j in range(10):
                page = Page(title=u'Page %s for root %s' % (j, i), parent=root)
                if j % 2:
                    page.visible = False
                page.save()

                for k in range(10):
                    subpage = Page(title=u'Subpage %s for page %s for root %s' % (k, j, i), parent=page)
                    if k % 2:
                        subpage.in_menu = False

                    subpage.save()


    def test_structure_init(self):
        """Инициализация структуры"""

        self._create_pages()

        #инициализация корня
        self.assertEqual(Structure().tree.title, u'ROOT')
        self.assertEqual(Structure(), Structure())


    def test_structure_content(self):
        """Проверка соотвествия дерева страниц дереву структуры"""

        self._create_pages()

        self.assertEqual(len(Structure().tree.children), 3)

        roots = Page.objects.root_nodes().filter(visible=True)
        for i in range(3):
            self.assertEqual(Structure().tree.children[i].title, roots[i].title)
            self.assertEqual(len(Structure().tree.children[i].children), 5)
            pages = roots[i].get_children().filter(visible=True)
            self.assertEqual(pages.count(), 5)

            for j in range(5):

                self.assertEqual(Structure().tree.children[i].children[j].title, pages[j].title)
                self.assertEqual(len(Structure().tree.children[i].children[j].children), 10)

                subpages = pages[j].get_children().filter(visible=True)
                self.assertEqual(subpages.count(), 10)

                for k in range(10):
                    self.assertEqual(Structure().tree.children[i].children[j].children[k].title, subpages[k].title)
                    self.assertEqual(Structure().tree.children[i].children[j].children[k].in_menu, subpages[k].in_menu)


    def test_serialize_structure_in_json(self):
        """Проверка сериализации структуры в json"""

        self._create_pages()

        self.assertTrue(Structure().get_structure_as_jsons())


    def test_regenerate_structure(self):
        """Обновление струтуры при изменении страниц"""

        self._create_pages()

        page = Page.objects.get(title=u'Subpage 5 for page 4 for root 1')
        strct_page = Structure().tree.children[1].children[2].children[5]

        self.assertEqual(page.title, strct_page.title)

        page.title = u'New page title'
        page.save()

        strct_page = Structure().tree.children[1].children[2].children[5]
        self.assertEqual(page.title, strct_page.title)

        page.title = u'New page title'
        page.in_menu = False
        page.save()

        strct_page = Structure().tree.children[1].children[2].children[5]
        self.assertEqual(page.title, strct_page.title)
        self.assertEqual(page.in_menu, strct_page.in_menu)


    def test_regenerate_structure_for_delete(self):
        """Обновление струтуры при удалении страниц"""

        self._create_pages()

        page = Page.objects.get(title=u'Subpage 5 for page 4 for root 1')
        strct_page = Structure().tree.children[1].children[2].children[5]

        self.assertEqual(page.title, strct_page.title)
        self.assertEqual(len(Structure().tree.children[1].children[2].children), 10)

        page.delete()

        self.assertEqual(len(Structure().tree.children[1].children[2].children), 9)

        for strct_page in Structure().tree.children[1].children[2].children:
            self.assertNotEquals(page.title, strct_page.title)


    def test_regenerate_structure_for_not_visible(self):
        """Обновление струтуры при скрытии страниц"""

        self._create_pages()

        page = Page.objects.get(title=u'Subpage 5 for page 4 for root 1')
        strct_page = Structure().tree.children[1].children[2].children[5]

        self.assertEqual(page.title, strct_page.title)
        self.assertEqual(len(Structure().tree.children[1].children[2].children), 10)

        page.visible = False
        page.save()

        self.assertEqual(len(Structure().tree.children[1].children[2].children), 9)

        for strct_page in Structure().tree.children[1].children[2].children:
            self.assertNotEquals(page.title, strct_page.title)


    def test_app_extension(self):
        """Ассоциирование странице модуля"""

        page = Page(
            title=u"Page title",
            app_extension=u'testapp',
            meta_title=u'page metatitle',
            meta_description=u'page meta descrption',
            meta_keywords=u'page meta keywords',
            parameters=u'light-blue.png'
        )
        page.save()

        struct_page=Structure().tree.children[0]

        self.assertEqual(struct_page.title, page.title)
        self.assertEqual(struct_page.get_url(), '/news/')
        self.assertEqual(struct_page.meta_title, page.meta_title)
        self.assertEqual(struct_page.meta_description, page.meta_description)
        self.assertEqual(struct_page.meta_keywords, page.meta_keywords)
        self.assertEqual(struct_page.parameters, {'page': page.parameters})


    def test_app_extension_children(self):
        """Ассоциирование странице модуля, структура модуля"""

        page = Page(
            title=u"Page title",
            app_extension=u'testapp_children',
        )
        page.save()

        children = [

            {
                'title': u'Node %s' % unicode(i),
                'url': u'url-for-node-%s' % unicode(i) ,
                'children': [],
                'in_menu': True,
                'parameters': {'par': i},
                'meta_title': u'Node %s title' % unicode(i),
                'meta_description': u'Node %s description' % unicode(i),
                'meta_keywords': u'Node %s keywords' % unicode(i),
            }
            for i in range(10)
        ]

        struct_page=Structure().tree.children[0]

        for i in range(10):
            self.assertEqual(struct_page.children[i].title, children[i]['title'])
            self.assertEqual(struct_page.children[i].get_url(), children[i]['url'])
            self.assertEqual(struct_page.children[i].parameters, children[i]['parameters'])
            self.assertEqual(struct_page.children[i].meta_title, children[i]['meta_title'])
            self.assertEqual(struct_page.children[i].meta_description, children[i]['meta_description'])
            self.assertEqual(struct_page.children[i].meta_keywords, children[i]['meta_keywords'])


    def test_app_extension_safe_for_structure(self):
        """Ассоциирование странице модуля, сохранение структуры страниц """

        page = Page(
            title=u"Page title",
            app_extension=u'testapp_safe_for_structure',
            meta_title=u'page metatitle',
            meta_description=u'page meta descrption',
            meta_keywords=u'page meta keywords',
            parameters=u'light-blue.png'
        )
        page.save()

        for i in range(10):
            node = Page(title=u'Node %s' % i, parent=page)
            node.save()

        pages = page.get_children()

        struct_page=Structure().tree.children[0]

        for i in range(10):
            self.assertEqual(struct_page.children[i].title, pages[i].title)


    def test_app_extension_override_parameters(self):
        """Ассоциирование странице модуля перекрытие параметров нода"""

        page = Page(
            title=u"Page title",
            app_extension=u'testapp_parameters',
            parameters=u'light-blue.png'
        )
        page.save()

        struct_page=Structure().tree.children[0]

        self.assertEqual(struct_page.title, page.title)
        self.assertEqual(struct_page.get_url(), '/news2/')
        self.assertEqual(struct_page.parameters, {'page': 'overrided page parameters', 'mod-value': 'mod-value'})


    def test_check_meta_params(self):
        """Проверка метаданных нода"""

        page = Page(
            title=u"Page title",
            meta_title=u'page metatitle',
            meta_description=u'page meta descrption',
            meta_keywords=u'page meta keywords',
            parameters=u'light-blue.png'
        )
        page.save()

        struct_page=Structure().tree.children[0]

        self.assertEqual(struct_page.meta_title, page.meta_title)
        self.assertEqual(struct_page.meta_description, page.meta_description)
        self.assertEqual(struct_page.meta_keywords, page.meta_keywords)
        self.assertEqual(struct_page.parameters['page'], page.parameters)


    def test_find_page_by_url(self):
        """Поиск нода структуры по урлу"""

        self._create_pages()

        pages = Page.objects.order_by('?')

        for page in pages:

            if not [p for p in page.get_ancestors(include_self=False) if p.visible==False]:
                struct_page = Structure().tree.get_element_by_url(page.get_absolute_url())
                if page.visible:
                    self.assertEqual(page.title, struct_page.title)
                else:
                    self.assertIsNone(struct_page)


    def test_get_ancestors_by_url(self):
        """Построение анцесторов по урлу"""

        self._create_pages()

        pages = Page.objects.filter(visible=True).order_by('?')

        for page in pages:
            if not [True for p in page.get_ancestors(include_self=True) if p.visible==False or p.in_menu == False]:
                self.assertEqual(
                    [p.title for p in page.get_ancestors(include_self=True)],
                    [s.title for s in Structure().tree.get_path_from_url(page.get_absolute_url())]
                )

        for page in pages:
            if not [True for p in page.get_ancestors(include_self=True) if p.visible==False]:
                self.assertEqual(
                    [p.title for p in page.get_ancestors(include_self=True)],
                    [s.title for s in Structure().tree.get_path_from_url(page.get_absolute_url(), check_in_menu=False)]
                )


#TestCase
class XendorSettingsTest(TestCase):

    def _prepare_for_test(self):

        obj1 = Setting(
            name=u'E-mail администратора',
            value=u'debug@yoursite.ru',
        )
        obj1.save()

        obj2 = Setting(
            name=u'Обратный e-mail',
            value=u'debug@yoursite.ru',
        )
        obj2.save()

    def test_init_settings(self):
        """Инциализация синглетона сеттингов"""

        self._prepare_for_test()

        XendorSettings()

        self.assertEqual(Setting.objects.all().count(), 2)

        self.assertEqual(XendorSettings().get(u'E-mail администратора'), u'debug@yoursite.ru')
        self.assertEqual(XendorSettings().get(u'Обратный e-mail'), u'debug@yoursite.ru')

    def test_add_in_settings(self):
        """Добавление настроек в синглетон"""
        self._prepare_for_test()

        XendorSettings().add_settings(u'Тестовая настройка', u'Значение тестовой настройки')
        XendorSettings().regenerate()

        self.assertEqual(Setting.objects.all().count(), 3)

        self.assertEqual(XendorSettings().get(u'Тестовая настройка'), u'Значение тестовой настройки')

    def test_settings_regenerate(self):
        """Регенерция сеттингов при изменении данных"""
        self._prepare_for_test()

        XendorSettings().regenerate()
        self.assertEqual(XendorSettings().get(u'E-mail администратора'), u'debug@yoursite.ru')


        setting_item = Setting.objects.get(name=u'E-mail администратора')
        setting_item.value = u'another.mail@yoursite.ru'
        setting_item.save()

        self.assertEqual(XendorSettings().get(u'E-mail администратора'), u'another.mail@yoursite.ru')


#TestCase
class MenuTest(TestCase):

    def _create_pages(self):
        """Создаем некоторое дерево страниц"""

        for i in range(2):
            root = Page(title = u'Root %s' % i)
            root.save()

            for j in range(7):
                page = Page(title=u'Page %s for root %s' % (j, i), parent=root)
                if j % 2:
                    page.visible = False
                page.save()

                for k in range(10):
                    subpage = Page(title=u'Subpage %s for page %s for root %s' % (k, j, i), parent=page)
                    if k % 2:
                        subpage.in_menu = False

                    subpage.save()

    def test_init_menu_by_main(self):
        """Инициализация меню от главной страницы"""

        self._create_pages()
        menu = Menu('/', parameters={'parent': 'MAIN'})

        self.assertEqual(len(menu.nodes), 4)

        root = Page.objects.get(is_main=True)
        children = root.get_children().filter(visible=True)
        for i in range(4):
            self.assertEqual(menu.nodes[i]['title'], children[i].title)


    def test_init_menu_by_page(self):
        """Инициализация меню от произвольной страницы страницы"""

        self._create_pages()

        for page in Page.objects.filter(visible=True, in_menu=True):
            ancestors = page.get_ancestors()
            if [True for p in ancestors if p.visible == False or p.in_menu == False]:
                self.assertRaises(Menu.MenuException, Menu, '/', parameters=_render_pars('parent=xendor-page&%s' % page.slug))
                continue

            menu = Menu('/', parameters=_render_pars('parent=xendor-page&%s' % page.slug))
            children = page.get_children().filter(visible=True, in_menu=True)
            self.assertEqual(children.count(), len(menu.nodes))
            for i in range(children.count()):
                self.assertEqual(children[i].title, menu.nodes[i]['title'])


    def test_init_menu_by_root(self):
        """Инициализация меню от корня"""

        self._create_pages()

        menu = Menu('/', parameters={'parent': 'ROOT'})

        self.assertEqual(len(menu.nodes), 2)
        self.assertEqual(len(menu.nodes[0]['children']), 0)
        self.assertEqual(len(menu.nodes[1]['children']), 0)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 2, 'show_children': True})

        self.assertEqual(len(menu.nodes), 2)
        self.assertEqual(len(menu.nodes[0]['children']), 4)
        self.assertEqual(len(menu.nodes[1]['children']), 4)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True})

        self.assertEqual(len(menu.nodes), 2)

        self.assertEqual(len(menu.nodes[0]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[0]['children'][i]['children']), 5)

        self.assertEqual(len(menu.nodes[1]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[1]['children'][i]['children']), 5)


    def test_check_title(self):
        """Проверка на соотвествие заголовков заголовкам меню"""

        self._create_pages()

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True})
        roots = Page.objects.root_nodes()
        for i in range(2):
            self.assertEqual(roots[i].title, menu.nodes[i]['title'])
            pages = roots[i].get_children().filter(visible=True)
            for j in range(4):
                self.assertEqual(pages[j].title, menu.nodes[i]['children'][j]['title'])
                subpages = pages[j].get_children().filter( in_menu=True)
                for k in range(5):
                    self.assertEqual(subpages[k].title, menu.nodes[i]['children'][j]['children'][k]['title'])

        changed_page = Page.objects.root_nodes()[0].get_children().filter(visible=True)[0]
        changed_page.menu_title=u'Menu title'
        changed_page.save()

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True})
        self.assertEqual(u'Menu title', menu.nodes[0]['children'][0]['title'])


    def test_active_and_current_node(self):
        """Проверка значений active и current в зависимости от текущего урла"""

        self._create_pages()

        active_page = Page.objects.root_nodes()[0].get_children().filter(visible=True)[0].get_children().filter(in_menu=True)[0]
        menu = Menu(active_page.get_absolute_url(), parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True})

        self.assertEqual(menu.nodes[0]['active'], True)
        self.assertEqual(menu.nodes[0]['children'][0]['active'], True)
        self.assertEqual(menu.nodes[0]['children'][0]['children'][0]['active'], True)
        self.assertEqual(menu.nodes[0]['children'][0]['children'][0]['current'], True)


        active_page = Page.objects.root_nodes()[1].get_children().filter(visible=True)[0].get_children().filter(in_menu=True)[3]
        menu = Menu(active_page.get_absolute_url(), parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True})

        self.assertEqual(menu.nodes[1]['active'], True)
        self.assertEqual(menu.nodes[1]['children'][0]['active'], True)
        self.assertEqual(menu.nodes[1]['children'][0]['children'][3]['active'], True)
        self.assertEqual(menu.nodes[1]['children'][0]['children'][3]['current'], True)

        self.assertEqual(menu.nodes[0]['children'][0]['active'], False)
        self.assertEqual(menu.nodes[0]['children'][0]['children'][3]['current'], False)


    def test_module_structure_in_menu(self):
        """Проверка параметров переданных из страниц и app_extend"""

        self._create_pages()

        mod_page = Page.objects.root_nodes()[0]
        mod_page.app_extension = 'testapp_children'
        mod_page.save()

        menu = Menu('/', parameters={'parent': 'MAIN', 'deep': 3, 'show_children': True})

        self.assertEqual(len(menu.nodes), 10)

        for i in range(10):
            self.assertEqual(menu.nodes[i]['title'], u'Node %s' % unicode(i))


    def test_parameters_for_menu(self):
        """Проверка параметров отображения меню: show_children, show_hidden"""

        self._create_pages()

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 3, 'show_children': True, 'show_hidden': True})

        self.assertEqual(len(menu.nodes), 2)

        self.assertEqual(len(menu.nodes[0]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[0]['children'][i]['children']), 10)

        self.assertEqual(len(menu.nodes[1]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[1]['children'][i]['children']), 10)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 2, 'show_children': True})

        self.assertEqual(len(menu.nodes), 2)

        self.assertEqual(len(menu.nodes[0]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[0]['children'][i]['children']), 0)

        self.assertEqual(len(menu.nodes[1]['children']), 4)
        for i in range(4):
            self.assertEqual(len(menu.nodes[1]['children'][i]['children']), 0)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 1, 'show_children': True})

        self.assertEqual(len(menu.nodes), 2)

        self.assertEqual(len(menu.nodes[0]['children']), 0)

        self.assertEqual(len(menu.nodes[1]['children']), 0)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': 0, 'show_children': True})
        self.assertEqual(len(menu.nodes), 0)

        menu = Menu('/', parameters={'parent': 'ROOT', 'deep': -1, 'show_children': True})
        self.assertEqual(len(menu.nodes), 0)


    def test_filtr_by_parameter(self):
        """Фильтр по параметрам страниц и app_extend"""

        self._create_pages()

        main = Page.objects.root_nodes()[0]
        main.app_extension = 'testapp_children'
        main.save()

        for i in range(10):
            menu = Menu('/', parameters=_render_pars('parent=MAIN;par=%s' % i))
            self.assertEqual(len(menu.nodes), 1)


    def test_validate_menu_parameters(self):

        self._create_pages()

        self.assertTrue(False)

#TestCase
class ViewTest(TestCase):

    def _create_pages(self):
        """Создаем некоторое дерево страниц"""

        for i in range(2):
            root = Page(title = u'Root %s' % i)
            root.save()

            for j in range(7):
                page = Page(title=u'Page %s for root %s' % (j, i), parent=root)
                if j % 2:
                    page.visible = False
                page.save()

                for k in range(10):
                    subpage = Page(title=u'Subpage %s for page %s for root %s' % (k, j, i), parent=page)
                    if k % 2:
                        subpage.in_menu = False

                    subpage.save()

    def test_main_page(self):
        """Проверка главной страницы"""

        self._create_pages()

        self.assertTrue(False)


    def test_other_pages(self):
        """Прочие страницы"""

        self._create_pages()

        self.assertTrue(False)


    def test_module_page(self):
        """Страница с ассоциированным модулем"""

        self._create_pages()

        self.assertTrue(False)


    def test_xendor_closed(self):
        """Проверка закрытого сеттингами сайта"""

        self._create_pages()

        self.assertTrue(False)


    def test_sitemap(self):
        """Сайтмапы"""

        self._create_pages()

        self.assertTrue(False)

    def test_check_301_in_menu_redirect(self):
        """Сайтмапы"""

        self._create_pages()

        self.assertTrue(False)