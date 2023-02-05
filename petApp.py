from flask import Flask, render_template, flash, session, redirect, url_for
from petForms import *
from petdb import *
from petLogger import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySecret'
logger = PetLogger.getLogger()


def checkIfUserExists(uname):
    return DBConnection.selectTable(ConfigVars.ownerTable, f"{DBConnection.ownerCols[1][0]} = '{uname}'")


def checkIfPetExists(pname):
    return DBConnection.selectTable(ConfigVars.petTable, f"{DBConnection.petCols[1][0]} = '{pname}'")


def checkIfUserAndPetExists(uname, pname):
    return (checkIfUserExists(uname), checkIfPetExists(pname))


@app.route('/')
def index():
    logger.info("Home page accessed")
    return render_template('pet_home.html', title='Home', id='nav1')


@app.route('/user', methods=['GET', 'POST'])
def registerUser():
    try:
        form = OwnerForm()
        if form.validate_on_submit():
            session['uname'] = form.name.data
            logger.info(f"Trying to insert owner {session.get('uname', None)} in table {ConfigVars.ownerTable}")
            user = checkIfUserExists(session.get('uname', None))
            if len(user) > 0:
                logger.warning(f'Owner {session["uname"]} already exists')
                flash(f'Owner {session["uname"]} already exists')
            else:
                DBConnection.insertTable(ConfigVars.ownerTable, [session.get('uname', None)])
                logger.info(f'Owner {session["uname"]} added')
                flash(f'Owner {session["uname"]} added')
            form.name.data = ''
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while registering user - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return render_template('register_user.html', form=form, title='Register User', id='nav5')


@app.route('/pet', methods=['GET', 'POST'])
def registerPet():
    form = PetForm()
    if form.validate_on_submit():
        try:
            session['pname'] = form.name.data
            session['price'] = form.price.data
            session['pcategory'] = form.category.data
            logger.info(f"Trying to insert pet {session.get('pname', None)} in table {ConfigVars.petTable}")
            pet = checkIfPetExists(session.get('pname', None))
            if len(pet) > 0:
                logger.warning(f'Pet {session.get("pname", None)} already exists')
                flash(f'Pet {session.get("pname", None)} already exists')
            else:
                DBConnection.insertTable(ConfigVars.petTable, [session.get('pname', None), session.get('price', None), session.get('pcategory', None)])
                logger.info(f'Pet {session["pname"]} of category {session["pcategory"]} and price {session["price"]} added')
                flash(f'Pet {session["pname"]} of category {session["pcategory"]} and price {session["price"]} added')
            form.name.data = ''
            form.category.data = ''
        except psycopg2.Error as pe:
            logger.exception(f"DB Error while registering pet - {pe}")
            return f"{pe}"
        except Exception as e:
            return f"{e}"
    return render_template('register_pet.html', form=form, title='Register Pet', id='nav6')


@app.route('/ownapet', methods=['GET', 'POST'])
def ownPet():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            uname = form.ownerName.data
            pname = form.petName.data
            logger.info(f'Trying to set owner of {pname} to {uname}')
            user, pet = checkIfUserAndPetExists(uname, pname)
            
            if len(user) == 0:
                logger.warning(f'The user {uname} does not exist')
                flash(f'The user {uname} does not exist')
            elif len(pet) == 0:
                logger.warning(f'The pet {pname} does not exist')
                flash(f'The pet {pname} does not exist')
            else:
                userid = user[0][0]
                petid = pet[0][0]
                owner = DBConnection.selectTable(ConfigVars.ownershipTable, f"{DBConnection.ownershipCols[1][0]} = {petid}")
                if len(owner) > 0:
                    ownerName = DBConnection.selectTable({ConfigVars.ownerTable}, f"{DBConnection.ownerCols[0][0]} = {owner[0][0]}")
                    logger.warning(f'Pet {pet[0][1]} already belongs to {ownerName[0][1]}')
                    flash(f'Pet {pet[0][1]} already belongs to {ownerName[0][1]}')
                else:
                    DBConnection.insertTable(ConfigVars.ownershipTable, [userid, petid])
                    logger.info(f'Pet {pet[0][1]} now belongs to {user[0][1]}')
                    flash(f'Pet {pet[0][1]} now belongs to {user[0][1]}')
            form.ownerName.data = ''
            form.petName.data = ''
        except psycopg2.Error as pe:
            logger.exception(f"DB Error while registering ownership - {pe}")
            return f"{pe}"
        except Exception as e:
            return f"{e}"
    return render_template('register_ownership.html', form=form, title='Register Ownership', id='nav7')


@app.route('/createTables', methods=['GET', 'POST'])
def createTables():
    try:
        DBConnection.createTables()
        logger.info('Tables created')
        flash('Tables created')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while creating tables - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return render_template('admin.html', title='Create Tables', id='nav8')


@app.route('/displayOwners', methods=['GET', 'POST'])
def dispOwners():
    try:
        rows = DBConnection.selectTable(tname=ConfigVars.ownerTable, additions=f" ORDER BY {DBConnection.ownerCols[0][0]}")
        logger.info('Displaying all owners')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while displaying owners - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return render_template('display_owners.html', rows=rows, title='Display users', id='nav3')


@app.route('/displayPets', methods=['GET', 'POST'])
def dispPets():
    try:
        rows = DBConnection.selectTable(tname=ConfigVars.petTable, additions=f" ORDER BY {DBConnection.petCols[0][0]}")
        logger.info('Displaying all pets')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while displaying pets - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return render_template('display_pets.html', rows=rows, title='Display Pets', id='nav4')


@app.route('/displayOwnership', methods=['GET', 'POST'])
def dispOwnership():
    try:
        rows = DBConnection.selectTable(tname=ConfigVars.ownershipTable, additions=f" GROUP BY {DBConnection.ownershipCols[0][0]}, {DBConnection.ownershipCols[1][0]} ORDER BY {DBConnection.ownershipCols[0][0]}, {DBConnection.ownershipCols[1][0]}")
        ownerships = []
        for row in rows:
            user = DBConnection.selectTable(ConfigVars.ownerTable, f"{DBConnection.ownerCols[0][0]} = {row[0]}")[0]
            pet = DBConnection.selectTable(ConfigVars.petTable, f"{DBConnection.petCols[0][0]} = {row[1]}")[0]
            ownerships.append((user[1], pet[1], pet[2], pet[3], user[0], pet[0]))
        logger.info('Displaying all ownerships')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while displaying ownerships - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return render_template('display_ownerships.html', rows=ownerships, title='Display Ownership', id='nav2')


@app.route('/deleteOwner/<ownerId>')
def deleteOwner(ownerId):
    try:
        DBConnection.deleteTable(ConfigVars.ownerTable, f"{DBConnection.ownerCols[0][0]}={ownerId}")
        logger.info(f'Deleted owner with id {ownerId}')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while deleting owner with id {ownerId} - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return redirect(url_for('dispOwners'))


@app.route('/deletePet/<petId>')
def deletePet(petId):
    try:
        DBConnection.deleteTable(ConfigVars.petTable, f"{DBConnection.petCols[0][0]}={petId}")
        logger.info(f'Deleted pet with id {petId}')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while deleting pet with id {petId} - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return redirect(url_for('dispPets'))


@app.route('/deleteOwnership/<petId>')
def deleteOwnership(petId):
    try:
        DBConnection.deleteTable(ConfigVars.ownershipTable, f"{DBConnection.ownershipCols[1][0]} = {petId}")
        logger.info(f'Deleted ownership of pet with id {petId}')
    except psycopg2.Error as pe:
        logger.exception(f"DB Error while deleting ownership of pet with id {petId} - {pe}")
        return f"{pe}"
    except Exception as e:
        return f"{e}"
    return redirect(url_for('dispOwnership'))


@app.route('/modifyOwner/<ownerId>', methods=['GET', 'POST'])
def modifyOwner(ownerId):
    form = OwnerForm()
    form.ownerId.data = ownerId
    if form.validate_on_submit():
        try:
            session['uname'] = form.name.data
            ownerId = int(form.ownerId.data)
            user = checkIfUserExists(session.get('uname', None))
            if len(user) > 0:
                logger.warning(f'Owner {session["uname"]} already exists')
                flash(f'Owner {session["uname"]} already exists')
            else:
                DBConnection.updateTable(ConfigVars.ownerTable, f"{DBConnection.ownerCols[1][0]}='{session.get('uname', None)}'", f"{DBConnection.ownerCols[0][0]}={ownerId}")
                logger.info(f'Owner name for id {ownerId} is now {session["uname"]}')
            form.name.data = ''
            form.ownerId.data = -1
        except psycopg2.Error as pe:
            logger.exception(f"DB Error while modifying owner with id {ownerId} - {pe}")
            return f"{pe}"
        except Exception as e:
            return f"{e}"
        return redirect(url_for('dispOwners'))
    return render_template('register_user.html', form=form, title='Modify User')


@app.route('/modifyPet/<petId>', methods=['GET', 'POST'])
def modifyPet(petId):
    form = PetForm()
    form.petId.data = petId
    if form.validate_on_submit():
        try:
            session['pname'] = form.name.data
            session['price'] = form.price.data
            session['pcategory'] = form.category.data
            petId = int(form.petId.data)
            pet = checkIfPetExists(session.get('pname', None))
            if len(pet) > 0:
                logger.warning(f'Pet {session.get("pname", None)} already exists')
                flash(f'Pet {session.get("pname", None)} already exists')
            else:
                setStr = f"{DBConnection.petCols[1][0]}='{session.get('pname', None)}', {DBConnection.petCols[2][0]}={session.get('price', None)}, {DBConnection.petCols[3][0]}='{session.get('pcategory', None)}'"
                DBConnection.updateTable(ConfigVars.petTable, setStr, f"{DBConnection.petCols[0][0]}={petId}")
                logger.info(f"Pet with id {petId} modified - {session['pname']}, {session['price']}, {session['pcategory']}")
            form.name.data = ''
            form.price.data = -1
            form.category.data = ''
            form.petId.data = -1
        except psycopg2.Error as pe:
            logger.exception(f"DB Error while modifying pet with id {petId} - {pe}")
            return f"{pe}"
        except Exception as e:
            return f"{e}"
        return redirect(url_for('dispPets'))
    return render_template('register_pet.html', form=form, title='Modify Pet')


@app.route('/modifyOwnership/<petId>/<petName>', methods=['GET', 'POST'])
def modifyOwnership(petId, petName):
    form = ModifyOwnershipForm()
    form.petId.data = petId
    if form.validate_on_submit():
        try:
            newName = form.ownerName.data
            petId = int(form.petId.data)
            user, pet = checkIfUserAndPetExists(newName, petName)
            
            if len(user) == 0 or len(pet) == 0:
                logger.warning(f'Owner {newName} does not exist')
                flash (f'Owner {newName} does not exist')
            else:
                owner = DBConnection.selectTable(ConfigVars.ownerTable, f"{DBConnection.ownerCols[1][0]}='{newName}'")[0]
                DBConnection.updateTable(ConfigVars.ownershipTable, f"{DBConnection.ownershipCols[0][0]}={owner[0]}", f"{DBConnection.ownershipCols[1][0]}={petId}")
                logger.info(f'Owner of pet {petName} is now {owner[1]}')
                form.petId.data = -1
                form.ownerName.data = ''
        except psycopg2.Error as pe:
            logger.exception(f"DB Error while modifying ownership of pet with id {petId} - {pe}")
            return f"{pe}"
        except Exception as e:
            return f"{e}"
        return redirect(url_for('dispOwnership'))
    return render_template('updateOwnership.html', petId=petId, petName=petName, form=form, title='Update Ownership')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)