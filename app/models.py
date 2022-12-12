from neo4j import GraphDatabase

from app.functions import edit_mother, edit_father, add_mother, add_father, add_spouse, edit_spouse, edit_siblings, \
    edit_children

driver = GraphDatabase.driver("neo4j+s://7bb30fdd.databases.neo4j.io", auth=("neo4j", "Pa$$w0rd"))


def create1(fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname):
    with driver.session() as session:
        if ddeath:
            session.run("CREATE (p:Person { fname: $fname, lname: $lname, dbirth: $dbirth, ddeath: $ddeath,"
                        "gender: $gender })", fname=fname, lname=lname, dbirth=dbirth, ddeath=ddeath, gender=gender)
        else:
            session.run("CREATE (p:Person { fname: $fname, lname: $lname, dbirth: $dbirth,gender: $gender })",
                        fname=fname, lname=lname, dbirth=dbirth, gender=gender)
        if mname:
            add_mother(fname, lname, mname, mlname)

        if dname:
            add_father(fname, lname, dname, dlname)

        if sname:
            add_spouse(fname, lname, sname, slname)


def edit1(id, fname, lname, dbirth, ddeath, gender, mname, dname, mlname, dlname, sname, slname, children):
    with driver.session() as session:
        session.run("MATCH (n) WHERE id(n) = $id SET n.fname = $fname, n.lname = $lname, n.dbirth = $dbirth, "
                    "n.ddeath = $ddeath, n.gender = $gender", id=int(id), fname=fname, lname=lname, dbirth=str(dbirth),
                    ddeath=ddeath, gender=gender)
        edit_mother(fname, lname, mname, mlname)
        edit_father(fname, lname, dname, dlname)
        edit_spouse(fname, lname, sname, slname)
        edit_siblings(fname,lname)
        edit_children(children, fname, lname)


def delete():
    with driver.session() as session:
        return session.run("MATCH (n {name: 'Andy'}) DETACH DELETE n")

