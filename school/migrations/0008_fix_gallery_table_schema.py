from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("school", "0007_add_learn_more_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                'ALTER TABLE "school_gallery" RENAME TO "school_gallery_old";',
                'CREATE TABLE "school_gallery" ('
                '"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, '
                '"title" varchar(200) NOT NULL, '
                '"image" varchar(100) NOT NULL, '
                '"description" text NOT NULL, '
                '"is_featured" bool NOT NULL, '
                '"created_at" datetime NOT NULL, '
                '"category_id" bigint NULL '
                'REFERENCES "school_gallerycategory" ("id") '
                'DEFERRABLE INITIALLY DEFERRED'
                ');',
                'INSERT INTO "school_gallery" ("id", "title", "image", "description", "is_featured", "created_at", "category_id") '
                'SELECT "id", "title", "image", "description", "is_featured", "created_at", "category_id" '
                'FROM "school_gallery_old";',
                'DROP TABLE "school_gallery_old";',
            ],
            reverse_sql=[
                'ALTER TABLE "school_gallery" RENAME TO "school_gallery_new";',
                'CREATE TABLE "school_gallery" ('
                '"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, '
                '"title" varchar(200) NOT NULL, '
                '"image" varchar(100) NOT NULL, '
                '"description" text NOT NULL, '
                '"category" varchar(100) NOT NULL, '
                '"is_featured" bool NOT NULL, '
                '"created_at" datetime NOT NULL, '
                '"category_id" INTEGER NULL'
                ');',
                'INSERT INTO "school_gallery" ("id", "title", "image", "description", "category", "is_featured", "created_at", "category_id") '
                'SELECT "id", "title", "image", "description", "category", "is_featured", "created_at", "category_id" '
                'FROM "school_gallery_new";',
                'DROP TABLE "school_gallery_new";',
            ],
        ),
    ]
