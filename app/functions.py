from datetime import datetime

from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j+s://7bb30fdd.databases.neo4j.io", auth=("neo4j", "Pa$$w0rd"))


def is_person(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (p { fname: $fname, lname: $lname }) RETURN p.fname", fname=fname,
                        lname=lname).data()
        if s:
            return True
        else:
            return False


def get_person(fname, lname):
    with driver.session() as session:
        return session.run("MATCH (p { fname: $fname, lname: $lname }) RETURN p", fname=fname, lname=lname)\
                            .data()[0]['p']


def get_id(fname, lname):
    with driver.session() as session:
        return session.run("MATCH (p { fname: $fname, lname: $lname }) RETURN ID(p)", fname=fname, lname=lname)\
            .data()[0]['ID(p)']


def get_person_by_id(id):
    with driver.session() as session:
        return session.run("MATCH (n) WHERE id(n) = $id RETURN n", id=int(id)).data()[0]['n']


def get_gender(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (p { fname: $fname, lname: $lname }) RETURN p.gender", fname=fname,
                        lname=lname).data()
        if s:
            return s[0]['p.gender']
        else:
            return ''


def get_birth(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (p { fname: $fname, lname: $lname }) RETURN p.dbirth", fname=fname,
                        lname=lname).data()
        if s:
            return s[0]['p.dbirth']
        else:
            return ''


def get_mother(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:CHILD]-(parent) "
                        "WHERE parent.gender = 'kobieta' RETURN parent", fname=fname, lname=lname).data()
        if s:
            return s[0]['parent']
        else:
            return


def get_father(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:CHILD]-(parent) "
                        "WHERE parent.gender = 'mężczyzna' RETURN parent", fname=fname, lname=lname).data()
        if s:
            return s[0]['parent']
        else:
            return


def get_spouse(fname, lname):
    with driver.session() as session:
        s = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:SPOUSE]-(spouse) RETURN spouse",
                        fname=fname, lname=lname).data()
        if s:
            return s[0]['spouse']
        else:
            return


def get_children(fname, lname):
    with driver.session() as session:
        children = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:PARENT]-(children) "
                               "RETURN children.fname, children.lname", fname=fname, lname=lname)
        if children:
            return children.data()
        else:
            return []


def get_siblings(fname, lname):
    with driver.session() as session:
        siblings = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:SIBLING]-(sibling) "
                               "RETURN sibling.fname, sibling.lname", fname=fname, lname=lname)
        if siblings:
            return siblings.data()
        else:
            return []


def validate(fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname):
    ok = True
    message = []

    if dbirth:
        if datetime.strptime(dbirth, '%Y-%m-%d') > datetime.today():
            message.append('Data urodzenia musi być późniejsza niż dzisiaj!')
            ok = False

    if ddeath:
        if datetime.strptime(dbirth, '%Y-%m-%d') > datetime.strptime(ddeath, '%Y-%m-%d'):
            message.append('Data śmierci musi być późniejsza od urodzenia!')
            ok = False
        if datetime.strptime(ddeath, '%Y-%m-%d') > datetime.today():
            message.append('Data śmierci musi być późniejsza niż dzisiaj!')
            ok = False
    if sname:
        if not slname:
            message.append('Dodaj nazwisko małżonka!')
            ok = False
        else:
            if is_person(sname, slname):
                if gender == get_gender(sname, slname):
                    ok = False
                    message.append('Twój małżonek musi być innej płci!')
            else:
                ok = False
                message.append('Nie ma małżonka w drzewie!')

    if dname:
        if not dlname:
            message.append('Dodaj nazwisko ojca!')
            ok = False
        else:
            if is_person(dname, dlname):
                if get_gender(dname, dlname) != 'mężczyzna':
                    message.append('Ojciec powinien być mężczyzną!')
                    ok = False
                if datetime.strptime(get_birth(dname, dlname), '%Y-%m-%d') > datetime.strptime(dbirth, '%Y-%m-%d'):
                    message.append('Ojciec powinien być starszy niż dodawana osoba!')
                    ok = False
            else:
                ok = False
                message.append('Nie ma ojca w drzewie!')

    if mname:
        if not mlname:
            message.append('Dodaj nazwisko matki!')
            ok = False
        else:
            if is_person(mname, mlname):
                if get_gender(mname, mlname) != 'kobieta':
                    message.append('Matka powinna być kobietą!')
                    ok = False

                if datetime.strptime(get_birth(mname, mlname), '%Y-%m-%d') > datetime.strptime(dbirth, '%Y-%m-%d'):
                    message.append('Matka powinna być starsza niż dodawana osoba!')
                    ok = False
            else:
                message.append('Nie ma matki w drzewie!')
                ok = False

    if slname:
        if not sname:
            message.append('Dodaj imię małżonka!')
            ok = False
    if dlname:
        if not dname:
            message.append('Dodaj imię ojca!')
            ok = False
    if mlname:
        if not mname:
            message.append('Dodaj imię matki!')
            ok = False

    if not fname or not lname or not dbirth or not gender:
        ok = False
        message.append('Uzupełnij wymagane pola!')

    return ok, message


def validate_children(children, gender, fname, lname):
    ok = True
    mss = []
    for c in children:
        if c['children.fname'] and c['children.lname']:
            if not is_person(c['children.fname'], c['children.lname']):
                ok = False
                mss.append("Dziecka " + c['children.fname'] + " " + c['children.lname'] + " nie ma w drzewie!")
            else:
                if gender == 'kobieta':
                    if get_mother(c['children.fname'], c['children.lname']):
                        if get_mother(c['children.fname'], c['children.lname'])['fname'] != fname and \
                                    get_mother(c['children.fname'], c['children.lname'])['lname'] != lname:
                            ok = False
                            mss.append("Dziecko " + c['children.fname'] + " " + c['children.lname'] +
                                       " posiada już matkę!")
                else:
                    if get_father(c['children.fname'], c['children.lname']):
                        if get_father(c['children.fname'], c['children.lname'])['fname'] != fname and \
                                get_father(c['children.fname'], c['children.lname'])['lname'] != lname:
                            ok = False
                            mss.append("Dziecko " + c['children.fname'] + " " + c['children.lname'] +
                                       " posiada już ojca!")

        elif c['children.fname'] and not c['children.lname']:
            ok = False
            mss.append("Brakuje nazwiska dziecka!")
        elif c['children.lname'] and not c['children.fname']:
            ok = False
            mss.append("Brakuje imienia dziecka!")
    return ok, mss


def add_mother(fname, lname, mname, mlname):
    with driver.session() as session:
        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND b.fname = $mname "
                    "AND b.lname = $mlname CREATE (a)-[r:PARENT]->(b)", fname=fname, lname=lname, mname=mname,
                    mlname=mlname)

        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $mname AND a.lname = $mlname AND "
                    "b.fname = $fname AND b.lname = $lname CREATE (a)-[r:CHILD]->(b)", fname=fname, lname=lname,
                    mname=mname, mlname=mlname)

        siblings = session.run("MATCH (a:Person {fname: $mname, lname: $mlname})<-[:PARENT]-(child) "
                               "RETURN child.fname, child.lname", mname=mname, mlname=mlname).data()
        print(siblings[1:])
        for s in siblings:
            if not(s['child.fname'] == fname and s['child.lname'] == lname):
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (a)-[r:SIBLING]->(b)", fname=fname,
                            lname=lname, fsname=s['child.fname'], lsname=s['child.lname'])
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (b)-[r:SIBLING]->(a)", fname=fname,
                            lname=lname, fsname=s['child.fname'], lsname=s['child.lname'])


def add_father(fname, lname, dname, dlname):
    with driver.session() as session:
        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND b.fname = $dname "
                    "AND b.lname = $dlname CREATE (a)-[r:PARENT]->(b)", fname=fname, lname=lname, dname=dname,
                    dlname=dlname)

        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $dname AND a.lname = $dlname AND b.fname = $fname"
                    " AND b.lname = $lname CREATE (a)-[r:CHILD]->(b)", fname=fname, lname=lname, dname=dname,
                    dlname=dlname)

        child = session.run("MATCH (a:Person {fname: $dname, lname: $dlname})<-[:PARENT]-(sibling) "
                                 "RETURN sibling.fname, sibling.lname", dname=dname, dlname=dlname).data()
        siblings = session.run("MATCH (a:Person {fname: $fname, lname: $lname})<-[:SIBLING]-(sibling) "
                                    "RETURN sibling.fname, sibling.lname", fname=fname, lname=lname).data()
        print(child[1:])
        print(siblings)
        for c in child:
            if c not in siblings and not (c['sibling.fname'] == fname and c['sibling.lname'] == lname):
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (a)-[r:SIBLING]->(b)", fname=fname,
                            lname=lname, fsname=c['sibling.fname'], lsname=c['sibling.lname'])
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (b)-[r:SIBLING]->(a)", fname=fname,
                            lname=lname, fsname=c['sibling.fname'], lsname=c['sibling.lname'])


def add_spouse(fname, lname, sname, slname):
    with driver.session() as session:
        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND b.fname = $sname "
                    "AND b.lname = $slname CREATE (a)-[r:SPOUSE]->(b)", fname=fname, lname=lname, sname=sname,
                    slname=slname)

        session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND b.fname = $sname "
                    "AND b.lname = $slname CREATE (b)-[r:SPOUSE]->(a)", fname=fname, lname=lname, sname=sname,
                    slname=slname)


def edit_mother(fname, lname, mname, mlname):
    if get_mother(fname, lname):
        if not (get_mother(fname, lname)['fname'] == mname and get_mother(fname, lname)['lname'] == mlname):
            pid = get_id(fname, lname)
            mid = get_id(get_mother(fname, lname)['fname'], get_mother(fname, lname)['lname'])
            with driver.session() as session:
                session.run("MATCH (p:Person)-[r:PARENT]-(m:Person) WHERE ID(p)=$pId  AND ID(m)= $mId DELETE r",
                            pId=int(pid), mId=int(mid))
                session.run("MATCH (p:Person)-[r:CHILD]-(m:Person) WHERE ID(m)=$mId  AND ID(p)= $pId DELETE r",
                            pId=int(pid), mId=int(mid))

            if mname:
                add_mother(fname, lname, mname, mlname)
    else:
        add_mother(fname, lname, mname, mlname)


def edit_father(fname, lname, dname, dlname):
    if get_father(fname, lname):
        if not (get_father(fname, lname)['fname'] == dname and get_father(fname, lname)['lname'] == dlname):
            pid = get_id(fname, lname)
            mid = get_id(get_father(fname, lname)['fname'], get_father(fname, lname)['lname'])
            with driver.session() as session:
                session.run("MATCH (p:Person)-[r:PARENT]-(m:Person) WHERE ID(p)=$pId  AND ID(m)= $mId DELETE r",
                            pId=int(pid), mId=int(mid))
                session.run("MATCH (p:Person)-[r:CHILD]-(m:Person) WHERE ID(m)=$mId  AND ID(p)= $pId DELETE r",
                            pId=int(pid), mId=int(mid))
                if dname:
                    add_father(fname, lname, dname, dlname)
    else:
        add_father(fname, lname, dname, dlname)


def edit_spouse(fname, lname, sname, slname):
    if get_spouse(fname, lname):
        if not (get_spouse(fname, lname)['fname'] == sname and get_spouse(fname, lname)['lname'] == slname):
            pid = get_id(fname, lname)
            sid = get_id(get_spouse(fname, lname)['fname'], get_spouse(fname, lname)['lname'])
            with driver.session() as session:
                session.run("MATCH (p:Person)-[r:SPOUSE]-(s:Person) WHERE ID(p)=$pId  AND ID(s)= $sId DELETE r",
                            pId=int(pid), sId=int(sid))
                if sname:
                    add_spouse(fname, lname, sname, slname)
    else:
        add_spouse(fname, lname, sname, slname)


def edit_siblings(fname, lname):
    siblings = get_siblings(fname, lname)
    mother = get_mother(fname, lname)
    father = get_father(fname, lname)
    siblings_m = []
    siblings_d = []
    if mother:
        siblings_m = get_children(mother['fname'], mother['lname'])
    if father:
        siblings_d = get_children(father['fname'], father['lname'])
    siblings_tmp = []

    for s in siblings_m:
        siblings_tmp.append([s['children.fname'], s['children.lname']])
    for s in siblings_d:
        t = [s['children.fname'], s['children.lname']]
        if t not in siblings_tmp:
            siblings_tmp.append(t)

    for s in siblings:
        t = [s['sibling.fname'], s['sibling.lname']]
        if t not in siblings_tmp:
            pid = get_id(fname, lname)
            sid = get_id(t[0], t[1])
            with driver.session() as session:
                session.run("MATCH (p:Person)-[r:SIBLING]-(s:Person) WHERE ID(p)=$pId  AND ID(s)= $sId DELETE r",
                            pId=int(pid), sId=int(sid))
    siblings1 = []
    for s in siblings:
        siblings1.append(list(s.values()))

    for s in siblings_tmp:
        if s not in siblings1 and not(s[0] == fname and s[1] == lname):
            with driver.session() as session:
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (a)-[r:SIBLING]->(b)", fname=fname,
                            lname=lname, fsname=s[0], lsname=s[1])
                session.run("MATCH (a:Person), (b:Person) WHERE a.fname = $fname AND a.lname = $lname AND  "
                            "b.fname = $fsname AND b.lname = $lsname CREATE (b)-[r:SIBLING]->(a)", fname=fname,
                            lname=lname, fsname=s[0], lsname=s[1])


def edit_children(children, fname, lname):
    child = get_children(fname, lname)
    child1 = []
    for c in child:
        child1.append(list(c.values()))
    for c in children:
        if c['children.fname'] and [c['children.fname'], c['children.lname']] not in child1:
            if get_gender(fname, lname) == 'kobieta':
                add_mother(c['children.fname'], c['children.lname'], fname, lname)
            else:
                add_father(c['children.fname'], c['children.lname'], fname, lname)
    children1 = []
    for c in children:
        children1.append(list(c.values()))
    for c in child1:
        if c not in children1:
            pid = get_id(fname, lname)
            cid = get_id(c[0], c[1])
            with driver.session() as session:
                session.run("MATCH (p:Person)-[r:PARENT]-(c:Person) WHERE ID(p)=$pId  AND ID(c)= $cId DELETE r",
                            pId=int(pid), cId=int(cid))
                session.run("MATCH (p:Person)-[r:CHILD]-(c:Person) WHERE ID(p)=$pId  AND ID(c)= $cId DELETE r",
                            pId=int(pid), cId=int(cid))


def delete1(fname, lname):
    with driver.session() as session:
        session.run("MATCH (n {fname: $fname, lname:$lname }) DETACH DELETE n", fname=fname, lname=lname)


def get_grandparents(fname, lname):
    with driver.session() as session:
        return session.run("MATCH (user:Person {fname: $fname, lname: $lname})-[r1:PARENT]->(parent) MATCH (parent)"
                           "-[r2:PARENT]-> (grandparent) RETURN grandparent.fname, grandparent.lname",
                           fname=fname, lname=lname).data()


def get_member(fname, lname, f1name, l1name):
    with driver.session() as session:
        return session.run("MATCH (n:Person {fname: $fname, lname: $lname}), "
                           "(m:Person {fname: $f1name, lname: $l1name}), "
                           "p = shortestPath((n)-[*]->(m)) WHERE length(p) >= 1 RETURN p",
                           fname=fname, lname=lname, f1name=f1name, l1name=l1name).data()[0]['p'][1::2]


def find_family(members, gender):
    zal = ''
    if len(members) == 1:
        if members[0] == 'PARENT' and gender == 'kobieta':
            zal = 'Matka'
        elif members[0] == 'PARENT' and gender == 'mężczyzna':
            zal = 'Ojciec'
        elif members[0] == 'CHILD' and gender == 'kobieta':
            zal = 'Córka'
        elif members[0] == 'CHILD' and gender == 'mężczyzna':
            zal = 'Syn'
        elif members[0] == 'SIBLING' and gender == 'kobieta':
            zal = 'Siostra'
        elif members[0] == 'SIBLING' and gender == 'mężczyzna':
            zal = 'Brat'
        elif members[0] == 'SPOUSE' and gender == 'kobieta':
            zal = 'Żona'
        else:
            zal = 'Mąż'
    elif len(members) == 2:
        if members[0] == 'PARENT':
            if members[1] == 'PARENT' and gender == 'kobieta':
                zal = 'Babcia'
            elif members[1] == 'PARENT' and gender == 'mężczyzna':
                zal = 'Dziadek'
            elif members[1] == 'SIBLING' and gender == 'kobieta':
                zal = 'Ciotka'
            elif members[1] == 'SIBLING' and gender == 'mężczyzna':
                zal = 'Wujek'
            elif members[1] == 'SPOUSE' and gender == 'kobieta':
                zal = 'Macocha'
            else:
                zal = 'Ojczym'
        elif members[0] == 'SIBLING':
            if members[1] == 'PARENT' and gender == 'kobieta':
                zal = 'Matka rodzeństwa'
            elif members[1] == 'PARENT' and gender == 'mężczyzna':
                zal = 'Ojciec rodzeństwa'
            elif members[1] == 'CHILD' and gender == 'kobieta':
                zal = 'Córka rodzeństwa'
            elif members[1] == 'CHILD' and gender == 'mężczyzna':
                zal = 'Syn rodzeństwa'
            elif members[1] == 'SIBLING' and gender == 'kobieta':
                zal = 'Siostra rodzeństwa'
            elif members[1] == 'SIBLING' and gender == 'mężczyzna':
                zal = 'Brat rodzeństwa'
            elif members[1] == 'SPOUSE' and gender == 'kobieta':
                zal = 'Żona rodzeństwa'
            else:
                zal = 'Mąż rodzeństwa'
        elif members[0] == 'SPOUSE':
            if members[0] == 'PARENT' and gender == 'kobieta':
                zal = 'Teściowa'
            elif members[0] == 'PARENT' and gender == 'mężczyzna':
                zal = 'Teść'
            elif members[0] == 'CHILD' and gender == 'kobieta':
                zal = 'Córka małżonka'
            elif members[0] == 'CHILD' and gender == 'mężczyzna':
                zal = 'Syn małżonka'
            elif members[0] == 'SIBLING' and gender == 'kobieta':
                zal = 'Siostra małżonka'
            elif members[0] == 'SIBLING' and gender == 'mężczyzna':
                zal = 'Brat małżonka'
        elif members[0] == 'CHILD':
            if members[0] == 'PARENT' and gender == 'kobieta':
                zal = 'Matka dziecka'
            elif members[0] == 'PARENT' and gender == 'mężczyzna':
                zal = 'Ojciec dziecka'
            elif members[0] == 'CHILD' and gender == 'kobieta':
                zal = 'Wnuczka'
            elif members[0] == 'CHILD' and gender == 'mężczyzna':
                zal = 'Wnuczek'
            elif members[0] == 'SIBLING' and gender == 'kobieta':
                zal = 'Siostra dziecka'
            elif members[0] == 'SIBLING' and gender == 'mężczyzna':
                zal = 'Brat dziecka'
            elif members[0] == 'SPOUSE' and gender == 'kobieta':
                zal = 'Synowa'
            else:
                zal = 'Zięć'
    else:
        for i in range(len(members)):
            if members[i] == 'PARENT':
                zal += 'Rodzic ->'
            elif members[i] == 'CHILD':
                zal += 'Dziecko ->'
            elif members[i] == 'SIBLING':
                zal += 'Rodzeństwo ->'
            else:
                zal += 'Małżonek ->'
        zal = zal[:-2]
    return zal
