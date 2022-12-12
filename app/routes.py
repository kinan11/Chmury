from app import app
from .functions import get_gender, get_birth, is_person, get_person, get_id, get_person_by_id, get_father, get_mother, \
    get_spouse, validate, get_siblings, get_children, validate_children, delete1, get_grandparents, get_member, \
    find_family
from .models import create1, delete, edit1
from flask import render_template, request, flash, redirect, url_for
from datetime import datetime


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        dbirth = request.form['dbirth']
        ddeath = request.form['ddeath']
        gender = request.form['gender']
        mname = request.form['mname']
        dname = request.form['dname']
        mlname = request.form['mlname']
        dlname = request.form['dlname']
        sname = request.form['sname']
        slname = request.form['slname']

        ok = True

        if dbirth:
            if datetime.strptime(dbirth, '%Y-%m-%d') > datetime.today():
                flash('Data urodzenia musi być późniejsza niż dzisiaj!')
                ok = False

        if ddeath:
            if datetime.strptime(dbirth, '%Y-%m-%d') > datetime.strptime(ddeath, '%Y-%m-%d'):
                flash('Data śmierci musi być późniejsza od urodzenia!')
                ok = False
            if datetime.strptime(ddeath, '%Y-%m-%d') > datetime.today():
                flash('Data śmierci musi być późniejsza niż dzisiaj!')
                ok = False
        if sname:
            if not slname:
                flash('Dodaj nazwisko małżonka!')
                ok = False
            else:
                if is_person(sname, slname):
                    if gender == get_gender(sname, slname):
                        ok = False
                        flash('Twój małżonek musi być innej płci!')
                else:
                    ok = False
                    flash('Nie ma małżonka w drzewie!')

        if dname:
            if not dlname:
                flash('Dodaj nazwisko ojca!')
                ok = False
            else:
                if is_person(dname, dlname):
                    if get_gender(dname, dlname) != 'mężczyzna':
                        flash('Ojciec powinien być mężczyzną!')
                        ok = False
                    if get_birth(dname, dlname) > dbirth:
                        flash('Ojciec powinien być starszy niż dodawana osoba!')
                        ok = False
                else:
                    ok = False
                    flash('Nie ma ojca w drzewie!')

        if mname:
            if not mlname:
                flash('Dodaj nazwisko matki!')
                ok = False
            else:
                if is_person(mname, mlname):
                    if get_gender(mname, mlname) != 'kobieta':
                        flash('Matka powinna być kobietą!')
                        ok = False
                    if get_birth(mname, mlname) > dbirth:
                        flash('Matka powinna być starsza niż dodawana osoba!')
                        ok = False
                else:
                    flash('Nie ma matki w drzewie!')
                    ok = False

        if slname:
            if not sname:
                flash('Dodaj imię małżonka!')
                ok = False
        if dlname:
            if not dname:
                flash('Dodaj imię ojca!')
                ok = False
        if mlname:
            if not mname:
                flash('Dodaj imię matki!')
                ok = False

        if not fname or not lname or not dbirth or not gender:
            ok = False
            flash('Uzupełnij wymagane pola!')

        if ok:
            create1(fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname)
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        if not is_person(fname, lname):
            flash("Nie ma takiej osoby w drzewie!")
        else:
            id = get_id(fname, lname)
            print(id)
            return redirect(url_for('edit2', id=id))
    return render_template('edit.html')


@app.route('/edit2/<id>', methods=["GET", "POST"])
def edit2(id):
    person = get_person_by_id(id)
    father = get_father(person['fname'], person['lname'])
    mother = get_mother(person['fname'], person['lname'])
    spouse = get_spouse(person['fname'], person['lname'])
    children = get_children(person['fname'], person['lname'])
    if father:
        person['dname'] = father['fname']
        person['dlname'] = father['lname']
    if mother:
        person['mname'] = mother['fname']
        person['mlname'] = mother['lname']
    if spouse:
        person['sname'] = spouse['fname']
        person['slname'] = spouse['lname']

    if request.method == 'POST':
        person['dname'] = request.form['dname']
        person['dlname'] = request.form['dlname']
        person['mname'] = request.form['mname']
        person['mlname'] = request.form['mlname']
        person['sname'] = request.form['sname']
        person['slname'] = request.form['slname']

        if request.form.get('child'):
            for i in range(int(request.form.get('child')) - len(children)):
                children.append({'children.fname': request.form[('cf' + str(int(request.form.get('child')) - i - 1))],
                                 'children.lname': request.form[('cl' + str(int(request.form.get('child')) - i - 1))]})
            children.append({'children.fname': '', 'children.lname': ''})

        if request.form.get('edit'):
            fname = request.form['fname']
            lname = request.form['lname']
            dbirth = request.form['dbirth']
            ddeath = request.form['ddeath']
            gender = request.form['gender']
            mname = request.form['mname']
            dname = request.form['dname']
            mlname = request.form['mlname']
            dlname = request.form['dlname']
            sname = request.form['sname']
            slname = request.form['slname']
            children = []
            if int(request.form.get('edit')) > 0:
                for i in range(int(request.form.get('edit'))):
                    children.append(
                        {'children.fname': request.form[('cf' + str(int(request.form.get('edit')) - i - 1))],
                         'children.lname': request.form[('cl' + str(int(request.form.get('edit')) - i - 1))]})

            ok, message = validate(fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname)
            ok1, message1 = validate_children(children, gender, fname, lname)

            if not(ok and ok1):
                ok = False
                message += message1

            if ok:
                edit1(id, fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname, children)
                return redirect(url_for('index'))
            else:
                for m in message:
                    flash(m)
    return render_template('edit2.html', person=person, children=children)


@app.route("/find", methods=["GET", "POST"])
def find():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        if not is_person(fname, lname):
            flash("Nie ma takiej osoby w drzewie!")

        else:
            id = get_id(fname, lname)
            return redirect(url_for('find1', id=id))
    return render_template('find.html')


@app.route("/find/<id>", methods=["GET", "POST"])
def find1(id):
    person = get_person_by_id(id)
    zal = []
    typ=''
    if request.method == 'POST':
        if request.form.get('mother'):
            mother = get_mother(person['fname'], lname=person['lname'])
            if mother:
                zal = [mother['fname'], mother['lname']]
                typ = 'mother'
            else:
                flash("Nie ma zarejestrowanej matki!")
                typ = 'error'
        if request.form.get('father'):
            father = get_father(person['fname'], lname=person['lname'])
            if father:
                zal = [father['fname'], father['lname']]
                typ = 'father'
            else:
                flash("Nie ma zarejestrowanego ojca!")
                typ = 'error'
        if request.form.get('brother'):
            siblings = get_siblings(person['fname'], lname=person['lname'])
            if siblings:
                for s in siblings:
                    print(s)
                    if get_gender(s['sibling.fname'], s['sibling.lname']) == 'mężczyzna':
                        zal.append([s['sibling.fname'], s['sibling.lname']])
                if len(zal) > 0:
                    typ = 'brother'
                else:
                    typ = 'error'
                    flash("Nie ma zarejestrowanego brata!")
            else:
                flash("Nie ma zarejestrowanego brata!")
                typ = 'error'

        if request.form.get('sister'):
            siblings = get_siblings(person['fname'], lname=person['lname'])
            if siblings:
                for s in siblings:
                    print(s)
                    if get_gender(s['sibling.fname'], s['sibling.lname']) == 'kobieta':
                        zal.append([s['sibling.fname'], s['sibling.lname']])
                if len(zal) > 0:
                    typ = 'sister'
                else:
                    typ = 'error'
                    flash("Nie ma zarejestrowanej siostry!")
            else:
                flash("Nie ma zarejestrowanej siostry!")
                typ = 'error'

        if request.form.get('grandmother'):
            grandparents = get_grandparents(person['fname'], lname=person['lname'])
            if grandparents:
                for g in grandparents:
                    if get_gender(g['grandparent.fname'], g['grandparent.lname']) == 'kobieta':
                        zal.append([g['grandparent.fname'], g['grandparent.lname']])
                if len(zal) > 0:
                    typ = 'grandmother'
                else:
                    typ = 'error'
                    flash("Nie ma zarejestrowanej babci!")
            else:
                flash("Nie ma zarejestrowanej babci!")
                typ = 'error'

        if request.form.get('grandfather'):
            grandparents = get_grandparents(person['fname'], lname=person['lname'])
            if grandparents:
                for g in grandparents:
                    if get_gender(g['grandparent.fname'], g['grandparent.lname']) == 'mężczyzna':
                        zal.append([g['grandparent.fname'], g['grandparent.lname']])
                if len(zal) > 0:
                    typ = 'grandmother'
                else:
                    typ = 'error'
                    flash("Nie ma zarejestrowanego dziadka!")
            else:
                flash("Nie ma zarejestrowanego dziadka!")
                typ = 'error'
        if request.form.get('family'):
            if is_person(request.form['fname'], request.form['lname']):
                members = get_member(person['fname'], person['lname'], request.form['fname'], request.form['lname'])
                gender = get_gender(request.form['fname'], request.form['lname'])
                typ = 'family'
                zal = find_family(members, gender)
            else:
                flash("Nie ma takiej osoby w drzewie!")
                typ='error'

    return render_template('find2.html', fname = person['fname'], lname=person['lname'], zal=zal, type=typ)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        if not is_person(fname, lname):
            flash("Nie ma takiej osoby w drzewie!")
        else:
            delete1(fname,lname)
            return redirect(url_for('index'))
    return render_template('delete.html')
